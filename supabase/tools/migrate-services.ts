// The service-schema runner of make migrate (plan T19, Question 3). Not built yet.
export interface ServiceMigration {
  service: string;
  version: string;
  file: string;
  sql: string;
  checksum: string;
}

export function serviceSchema(service: string): string {
  throw new Error(`serviceSchema(${service}): not built yet`);
}

export function serviceMigrations(servicesDir: string): ServiceMigration[] {
  throw new Error(`serviceMigrations(${servicesDir}): not built yet`);
}

export function schemaProblems(service: string, sql: string): string[] {
  throw new Error(`schemaProblems(${service}, ${sql.length} characters): not built yet`);
}
