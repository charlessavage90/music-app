// Two jobs on one viewer-request function.
//
// 1. The front-door check (PW-7, replacing DEP-4's shared password). This is
//    not authentication and never was: it is a shared secret in a function
//    body. Its purpose is narrower than the password's and more precise —
//    ensure every request has passed through Cloudflare, where the rate limit
//    lives. Without it the generated CloudFront address answers directly and
//    the rate limit is decorative, which is TR-7's defect one layer up: a
//    control on the front door while the origin answers on its own name.
//
//    A request WITHOUT the secret is redirected to the real hostname rather
//    than refused, because the overwhelmingly likely cause is a link shared
//    before this change. A 403 would break every one of them. The exception is
//    a request that already carries the right Host — there, a redirect is an
//    infinite loop, so it fails closed.
//
// 2. The SPA fallback (TR-5). Without it every shared journey link 403s: the
//    default behaviour serves a private S3 bucket, which holds no object at
//    /path/<mbid>/<mbid>. It lives here rather than in the distribution's
//    errorResponses because those are distribution-level and would rewrite
//    the API's own 404s and the origin-secret 403 into an HTML page with
//    status 200 (TKB-2).
//
// __FRONT_DOOR_SECRET__ and __SITE_HOSTNAME__ are substituted at synth time
// from DeployInputs. The secret is never in git.

var REFUSAL_BODY =
  '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>artistpath</title></head>' +
  '<body style="font-family:system-ui,sans-serif;max-width:32rem;' +
  'margin:4rem auto;padding:0 1rem;line-height:1.5">' +
  '<h1>artistpath</h1>' +
  '<p>This request did not arrive through the front door, so it was refused.</p>' +
  '<p>If you followed a link and reached this page, please report it.</p>' +
  '</body></html>';

// CloudFront Functions give the query string as an object and provide no
// serialiser. Bypass state lives in it (/path/:from/:to?dislike=…&known=…), so
// a redirect that drops it silently changes the journey the recipient sees.
function queryString(qs) {
  var parts = [];
  for (var key in qs) {
    var v = qs[key];
    if (v.multiValue) {
      for (var i = 0; i < v.multiValue.length; i++) {
        parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(v.multiValue[i].value));
      }
    } else {
      parts.push(encodeURIComponent(key) + '=' + encodeURIComponent(v.value));
    }
  }
  return parts.length ? '?' + parts.join('&') : '';
}

function handler(event) {
  var request = event.request;
  var headers = request.headers;

  var supplied = headers['x-front-door'] && headers['x-front-door'].value;
  if (supplied !== '__FRONT_DOOR_SECRET__') {
    var host = headers.host && headers.host.value;
    if (host === '__SITE_HOSTNAME__') {
      // Already on the right name and still no secret: Cloudflare has been
      // bypassed, or the Transform Rule is gone. Redirecting here would loop.
      return {
        statusCode: 403,
        statusDescription: 'Forbidden',
        headers: { 'content-type': { value: 'text/html; charset=utf-8' } },
        body: { encoding: 'text', data: REFUSAL_BODY },
      };
    }
    return {
      statusCode: 301,
      statusDescription: 'Moved Permanently',
      headers: {
        location: {
          value: 'https://__SITE_HOSTNAME__' + request.uri + queryString(request.querystring),
        },
      },
    };
  }

  // Anything that is not an API call and has no file extension is an SPA
  // route: /path/<mbid>/<mbid> holds no S3 object.
  //
  // /health needs no case here. Only /api/* is routed to App Runner, so
  // /health is not reachable through CloudFront at all — it is reached at the
  // App Runner origin URL, which is where App Runner's own health checker
  // reaches it and where design §9's identity check is run.
  var uri = request.uri;
  if (uri.indexOf('/api/') !== 0 && uri.lastIndexOf('.') <= uri.lastIndexOf('/')) {
    request.uri = '/index.html';
  }
  return request;
}
