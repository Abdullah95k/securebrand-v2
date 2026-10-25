// How the services use the fold. normalize-item's fallback (lang-dialect-id 8): while lang-dialect-id
// is unreachable, an item is published with lang "und", text_norm from this fold and lang_pending, and
// lang_rescore corrects it later. keyword-matcher compiles every keyword form under both folds
// (keyword-matcher 5.3 B) and reports offsets in code points of text_norm.
import { FOLD_VERSION, fold, textNorm, tokenize } from "text";

const item = { title: null, text: "شبكة زين بالبصرة ضعيفة اليوم 😡 #زين_العراق" };
const normalized = {
  lang: "und",
  lang_pending: true,
  text_norm: textNorm(item.title, item.text, "und"),
  fold: FOLD_VERSION,
};
console.log(JSON.stringify(normalized));

for (const form of ["زين العراق", "#زين_العراق", "كوردستان", "وڵاتێكي"]) {
  console.log(`${form}: ar ${fold(form, "ar")} | ckb ${fold(form, "ckb")}`);
}

const spans = tokenize(normalized.text_norm).map((t) => `${t.text} [${t.start}, ${t.end})`);
console.log(spans.join(" · "));
