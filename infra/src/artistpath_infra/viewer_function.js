// Two jobs on one viewer-request function.
//
// 1. The shared-password gate (DEP-4). This is a shared secret in a function
//    body, not authentication: no per-user identity, and it secures nothing.
//    Its purpose is narrow — every card view fires an unrate-limited clip
//    lookup against Deezer/iTunes, and a rate-limited catalogue presents as
//    silent cards, visually identical to the C1 wrong-artist defect closed on
//    2026-07-25. The gate exists so a forwarded link cannot produce a symptom
//    that would be diagnosed as a regression in closed work.
//
// 2. The SPA fallback (TR-5). Without it every shared journey link 403s: the
//    default behaviour serves a private S3 bucket, which holds no object at
//    /path/<mbid>/<mbid>. It lives here rather than in the distribution's
//    errorResponses because those are distribution-level and would rewrite
//    the API's own 404s and the origin-secret 403 into an HTML page with
//    status 200 (TKB-2).
//
// __EXPECTED_AUTH__ is substituted at synth time from the environment. It is
// never in git. __EXPECTED_USERNAME__ is substituted from the same constant the
// credential is built from (stack.py's SITE_USERNAME), so the name below cannot
// drift from the name the gate admits.
//
// FRO-2 / RMD-11: the browser asks for a username and a password, only the
// password is ever shared, and until 2026-07-27 the 401 carried no body — so
// the first attempt of the first real visitor was spent guessing. Naming the
// username discloses nothing: this is a shared password, not authentication
// (see 1 above). The password is NOT named here, and a test asserts the whole
// response does not contain it.
var REFUSAL_BODY =
  '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>artistpath</title></head>' +
  '<body style="font-family:system-ui,sans-serif;max-width:32rem;' +
  'margin:4rem auto;padding:0 1rem;line-height:1.5">' +
  '<h1>artistpath</h1>' +
  '<p>This site is password-protected while it is being shared privately.</p>' +
  '<p>The username is <strong>__EXPECTED_USERNAME__</strong>.</p>' +
  '<p>The password was sent to you separately. Reload the page to try again.</p>' +
  '</body></html>';

function handler(event) {
  var request = event.request;
  var headers = request.headers;

  // TEMPORARY — PW-6 step 6 check 4. Proves the Cloudflare front-door header
  // reaches this function BEFORE PW-7 makes the site depend on it. Reported as
  // a response header on the 401 below, PRESENCE ONLY — never the value, which
  // is the shared secret. NOT console.log: a CloudFront Function's stdout is
  // what the test harness parses as JSON, so logging breaks 10 tests.
  // PW-7 replaces this with the enforcing check. Remove it then.
  var frontDoorPresent = headers['x-front-door'] ? '1' : '0';

  if (!headers.authorization || headers.authorization.value !== '__EXPECTED_AUTH__') {
    return {
      statusCode: 401,
      statusDescription: 'Unauthorized',
      headers: {
        'www-authenticate': { value: 'Basic realm="artistpath"' },
        'content-type': { value: 'text/html; charset=utf-8' },
        // TEMPORARY, PW-6 check 4 — see the note at the top of handler().
        'x-front-door-probe': { value: frontDoorPresent },
      },
      body: { encoding: 'text', data: REFUSAL_BODY },
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
