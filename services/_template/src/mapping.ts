// Pure functions from the records the adapter returns to the service's outputs. No I/O, so fixture
// tests cover them completely. Outputs use the contract types from packages/contracts (never a
// local copy) and carry provenance (route, vendor, service, fetched_at) and retention_class.
export type Mapper<Record, Output> = (record: Record) => Output;

export function mapAll<Record, Output>(
  records: readonly Record[],
  map: Mapper<Record, Output>,
): Output[] {
  return records.map((record) => map(record));
}
