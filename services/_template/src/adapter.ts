// The adapter is the only module that talks to the outside world: a platform API, a vendor, a
// crawled site. Write it the way docs/patterns/ADAPTER-PATTERN.md (from C0) shows. Every external
// call goes through listening-sdk's HTTP adapter base (F5), which applies the error policy (429
// backs off 30 s to 15 min with jitter; 401 and 403 mark the route degraded and stop the batch;
// empty 200s are counted), the quota client and the canary hook. Tests replace the adapter with
// recorded fixtures or the fake platform, never the network.
export interface Adapter<Request, Record> {
  fetch(request: Request): Promise<readonly Record[]>;
}
