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
// never in git.
function handler(event) {
  var request = event.request;
  var headers = request.headers;

  if (!headers.authorization || headers.authorization.value !== '__EXPECTED_AUTH__') {
    return {
      statusCode: 401,
      statusDescription: 'Unauthorized',
      headers: {
        'www-authenticate': { value: 'Basic realm="artistpath"' },
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
