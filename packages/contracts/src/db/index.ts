// The control plane's database contract (F3, Question 7): the row types generated from
// supabase/migrations, and the leader-election lock key. Import from "contracts/db".
export { LEADER_LOCK_NAMESPACE, leaderLockKey } from "./leader-lock.ts";
