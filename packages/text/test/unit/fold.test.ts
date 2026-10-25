// The fold's behaviour as the plan's acceptance map names it (docs/plans/F7.md): lang-dialect-id
// section 13 as far as a library can prove it, the brief's "Watch for" and the uncovered behaviours.
import { describe, expect, it, vi } from "vitest";
import { fold, textNorm, TextError } from "../../src/index.ts";
import { corpus } from "../helpers.ts";

// The letters whose spelling differs between the two folds, written as escapes so that no font can
// hide which one a test means.
const KAF_AR = "\u{643}"; // ك
const KAF_FA = "\u{6A9}"; // ک
const YEH_AR = "\u{64A}"; // ي
const YEH_FA = "\u{6CC}"; // ی
const ALEF_MAKSURA = "\u{649}"; // ى

function textError(f: () => unknown): TextError {
  try {
    f();
  } catch (e) {
    if (e instanceof TextError) return e;
    throw e;
  }
  throw new Error("no TextError was thrown");
}

describe("lang-dialect-id 13, criterion 1: the examples of section 6.2", () => {
  it("folds both examples of section 6.2 exactly", () => {
    expect(fold("النت منقطع بالبصرة من الصبح، شنو السالفة؟", "ar")).toBe(
      "النت منقطع بالبصره من الصبح شنو السالفه",
    );
    // "The second record arrived as ... typed with Arabic yaa."
    const typed = `ئاو${YEH_AR} خواردنەوە ن${YEH_AR}${YEH_AR}ە لە بەسرە`;
    expect(fold(typed, "ckb")).toBe(`ئاو${YEH_FA} خواردنەوە ن${YEH_FA}${YEH_FA}ە لە بەسرە`);
  });
});

describe("criterion 2: language is decided first, and the fold depends on it", () => {
  const sorani = `${KAF_FA}وردستان وڵاتێ${KAF_FA}${YEH_FA} جوانە`;
  const withArabicLetters = `${KAF_AR}وردستان وڵاتێ${KAF_AR}${YEH_AR} جوانە`;

  it("folds the Sorani sentence typed with Arabic kaf and yaa to the Sorani spelling under ckb", () => {
    expect(fold(sorani, "ckb")).toBe(sorani);
    expect(fold(withArabicLetters, "ckb")).toBe(sorani);
  });

  it("refuses a call without a language label", () => {
    // @ts-expect-error: the label is required, so a caller that folds before detecting does not compile
    expect(textError(() => fold(sorani)).code).toBe("no_lang");
  });
});

describe("criterion 3: the Iraqi letters", () => {
  it("keeps چ گ پ ڤ ژ in Iraqi Arabic text", () => {
    for (const word of [
      "الچاي حار",
      "گاع ما اكو انترنت",
      "پاسپورت جديد",
      "ڤايبر واقف",
      "ژيلاتين",
    ]) {
      expect(fold(word, "ar")).toBe(word);
    }
  });

  it("turns ک into ك in Arabic text", () => {
    expect(fold(`شب${KAF_FA}ة زين ضعيفة`, "ar")).toBe(`شب${KAF_AR}ه زين ضعيفه`);
    expect(fold(`ا${KAF_FA}و انترنت`, "ar")).toBe(`ا${KAF_AR}و انترنت`);
  });
});

describe("criterion 5: no dialect input", () => {
  it("the fold's output depends only on text and lang", () => {
    expect(fold.length).toBe(2);
    const first = fold("خدمة زين بالموصل", "ar");
    fold(`${KAF_AR}وردستان`, "ckb");
    fold("Shlonak", "en");
    expect(fold("خدمة زين بالموصل", "ar")).toBe(first);
  });
});

describe("criteria 8, 9 and 11: normalize-item's fallback under und (PRD 8)", () => {
  it("under und applies the Arabic fold with the Sorani-token override", () => {
    const input = `${KAF_AR}وردستان وڵاتێ${KAF_AR}${YEH_AR} جوانە`;
    // كوردستان holds no Sorani-only letter, so it keeps the Arabic fold until lang_rescore.
    expect(fold(input, "und")).toBe(`${KAF_AR}وردستان وڵاتێ${KAF_FA}${YEH_FA} جوانە`);
    expect(fold(input, "ar")).toBe(fold(input, "und"));
  });
});

describe("criterion 10: no text in logs", () => {
  it("folding the corpus writes nothing to stdout or stderr", () => {
    const spies = [
      vi.spyOn(process.stdout, "write"),
      vi.spyOn(process.stderr, "write"),
      vi.spyOn(console, "log"),
      vi.spyOn(console, "info"),
      vi.spyOn(console, "warn"),
      vi.spyOn(console, "error"),
      vi.spyOn(console, "debug"),
    ];
    try {
      for (const c of corpus()) textNorm(c.title, c.text, c.lang);
      for (const spy of spies) expect(spy).not.toHaveBeenCalled();
    } finally {
      for (const spy of spies) spy.mockRestore();
    }
  });
});

describe("the brief's Watch for", () => {
  it("yaa and kaf fold toward Arabic under ar and toward Sorani under ckb", () => {
    const input = `م${KAF_AR}تب م${KAF_FA}تب عل${YEH_AR} عل${YEH_FA} عل${ALEF_MAKSURA}`;
    expect(fold(input, "ar")).toBe(`م${KAF_AR}تب م${KAF_AR}تب عل${YEH_AR} عل${YEH_AR} عل${YEH_AR}`);
    expect(fold(input, "ckb")).toBe(
      `م${KAF_FA}تب م${KAF_FA}تب عل${YEH_FA} عل${YEH_FA} عل${YEH_FA}`,
    );
  });

  it("Arabizi is only case-folded, never transliterated", () => {
    expect(fold("Shlonak 7abibi, SHAKU MAKU?", "en")).toBe("shlonak 7abibi shaku maku");
    expect(fold("Shlonak 7abibi", "und")).toBe("shlonak 7abibi");
  });
});

describe("bad input (D8)", () => {
  it("refuses a lone surrogate with not_unicode", () => {
    expect(textError(() => fold("سلام \uD83D", "ar")).code).toBe("not_unicode");
    expect(textError(() => fold("\uDE00 سلام", "ckb")).code).toBe("not_unicode");
    expect(textError(() => textNorm("\uD800", "سلام", "ar")).code).toBe("not_unicode");
  });

  it("an empty, whitespace-only or emoji-only text folds to the empty string", () => {
    expect(fold("", "ar")).toBe("");
    expect(fold(" \n\t\u{A0}\u{3000}", "ckb")).toBe("");
    expect(fold("😂😂👍\u{1F3FB}", "und")).toBe("");
    expect(fold("❤\u{FE0F}🇮🇶 1\u{FE0F}\u{20E3}", "ar")).toBe("1");
    expect(fold("❤\u{FE0F}🇮🇶", "ar")).toBe("");
  });

  it("refuses a label outside contracts' LANG_LABELS", () => {
    // @ts-expect-error: "fa" is not one of contracts' LANG_LABELS
    expect(textError(() => fold("سلام", "fa")).code).toBe("bad_lang");
  });

  it("refuses a text that is not a string", () => {
    // @ts-expect-error: the text must be a string
    expect(textError(() => fold(null, "ar")).code).toBe("not_string");
  });

  it("textNorm refuses a missing or bad label even when there is nothing to fold", () => {
    // @ts-expect-error: the label is required
    expect(textError(() => textNorm(null, null, undefined)).code).toBe("no_lang");
    // @ts-expect-error: "fa" is not one of contracts' LANG_LABELS
    expect(textError(() => textNorm("", "", "fa")).code).toBe("bad_lang");
    // @ts-expect-error: the title must be a string
    expect(textError(() => textNorm(7, null, "ar")).code).toBe("not_string");
  });
});

describe("title and text", () => {
  it("text_norm joins the folded title and text with one space, title first, skipping an empty one", () => {
    expect(textNorm("خبر عاجل!", "الكهرباء مقطوعة", "ar")).toBe("خبر عاجل الكهرباء مقطوعه");
    expect(textNorm(null, "الكهرباء مقطوعة", "ar")).toBe("الكهرباء مقطوعه");
    expect(textNorm("😂", "الكهرباء مقطوعة", "ar")).toBe("الكهرباء مقطوعه");
    expect(textNorm("هەواڵ", null, "ckb")).toBe("هەواڵ");
    expect(textNorm(undefined, "", "und")).toBe("");
  });
});

describe("oversize text (PRD 8, E4)", () => {
  it("a text of several megabytes with URLs, hashtags and Sorani tokens folds in full, equals the fold of its chunks joined by one space, and finishes within 10 seconds", () => {
    const samples = [
      ...corpus().map((c) => c.text),
      "شوفوا https://example.com/news?id=7 عن #البصرة_تنتفض و@example_news",
      "سەردانی www.example.org/krd بکەن، #هەولێر_جوانە",
    ];
    const chunks: string[] = [];
    let bytes = 0;
    for (let i = 0; bytes < 4 * 1024 * 1024; i += 1) {
      const chunk = samples[i % samples.length] ?? "";
      chunks.push(chunk);
      bytes += Buffer.byteLength(chunk, "utf8") + 1;
    }
    const big = chunks.join("\n");
    expect(Buffer.byteLength(big, "utf8")).toBeGreaterThan(4 * 1024 * 1024);
    for (const lang of ["und", "ckb"] as const) {
      const reference = chunks
        .map((chunk) => fold(chunk, lang))
        .filter((s) => s !== "")
        .join(" ");
      const started = performance.now();
      const folded = fold(big, lang);
      const elapsed = performance.now() - started;
      expect(folded).toBe(reference);
      expect(elapsed).toBeLessThan(10_000);
    }
  });
});
