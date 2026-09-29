# Failure Analysis - 50 QA - Hybrid RRF

Total QA: 50, Failed at R@5: 13 (26.0%)

## Category counts
- exact_article_mismatch: 12
- urdu_mixed_query: 1
- semantic_drift: 0
- chunk_boundary: 0

## Failed cases (Top 13)

### en_01 - Rank >10 - Lang en
Q: What does Article 9 of Constitution say about security of person?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p12
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: No person shall be deprived of life or liberty save in accordance with law.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### ur_01 - Rank >10 - Lang ur
Q: پاکستان پینل کوڈ دفعہ 379 کے تحت چوری کی سزا کیا ہے؟

Gold: PAKISTANCODE__Pakistan_Penal_Code_1860.pdf p85
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: Imprisonment up to three years or fine or both.

Hypothesis: Multilingual embedding weak for Urdu, needs better Urdu model

---

### ur_02 - Rank >10 - Lang ur
Q: آرٹیکل 10 گرفتاری اور حراست کے بارے میں کیا تحفظ فراہم کرتا ہے؟

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p22
Got Top1: PAKISTANCODE__Pakistan_Penal_Code_18602026-09-27EN_Under_Review.txt
Gold answer snippet: No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice.

Hypothesis: Multilingual embedding weak for Urdu, needs better Urdu model

---

### mix_02 - Rank 8 - Lang mixed
Q: Article 10 mein giraftari aur hirasat ke baare mein kya tahaffuz diya gaya hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p22
Got Top1: PAKISTANCODE__Code_of_Civil_Procedure_19082026-09-27EN_Under_Review.txt
Gold answer snippet: No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### ur_05 - Rank >10 - Lang ur
Q: آرٹیکل 19 اظہار رائے کی آزادی کے بارے میں کیا کہتا ہے؟

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p30
Got Top1: PAKISTANCODE__Pakistan_Penal_Code_18602026-09-27EN_Under_Review.txt
Gold answer snippet: Every citizen shall have the right to freedom of speech and expression, and there shall be freedom of the press, subject to any reasonable restrictions imposed by law in the interest of the glory of Islam or the integrity, security or defence of Pakistan.

Hypothesis: Multilingual embedding weak for Urdu, needs better Urdu model

---

### ur_06 - Rank >10 - Lang ur
Q: آرٹیکل 19 اے معلومات تک رسائی کے بارے میں کیا ضمانت دیتا ہے؟

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p31
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: Every citizen shall have the right to have access to information in all matters of public importance subject to regulation and reasonable restrictions imposed by law.

Hypothesis: Multilingual embedding weak for Urdu, needs better Urdu model

---

### en_09 - Rank >10 - Lang en
Q: What is stated in Article 9 about security of person?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p20
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: No person shall be deprived of life or liberty save in accordance with law.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### mix_09 - Rank >10 - Lang mixed
Q: Article 9 mein security of person ka kya matlab hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p20
Got Top1: PAKISTANCODE__Rules_of_Business_19732026-09-27__EN__Under_Review.txt
Gold answer snippet: No person shall be deprived of life or liberty save in accordance with law.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### ur_12 - Rank >10 - Lang ur
Q: آرٹیکل 16 جلسہ کی آزادی کے بارے میں کیا کہتا ہے؟

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p27
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: Every citizen shall have the right to assemble peacefully and without arms, subject to any reasonable restrictions imposed by law in the interest of public order.

Hypothesis: Multilingual embedding weak for Urdu, needs better Urdu model

---

### mix_15 - Rank >10 - Lang mixed
Q: Article 23 mein property ke haq ke baare mein kya likha hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p34
Got Top1: PAKISTANCODE__Code_of_Civil_Procedure_19082026-09-27EN_Under_Review.txt
Gold answer snippet: Every citizen shall have the right to acquire, hold and dispose of property in any part of Pakistan, subject to the Constitution and any reasonable restrictions imposed by law in the public interest.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### mix_16 - Rank 10 - Lang mixed
Q: Article 25A ke tehat muft taleem ki umar kya hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p36
Got Top1: PAKISTANCODE__Pakistan_Penal_Code_18602026-09-27EN_Under_Review.txt
Gold answer snippet: The State shall provide free and compulsory education to all children of the age of five to sixteen years in such manner as may be determined by law.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### mix_19 - Rank 6 - Lang mixed
Q: Article 10 mein giraftar shaks ko kya haq hasil hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p22
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: No person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest, nor shall he be denied the right to consult and be defended by a legal practitioner of his choice.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

### mix_20 - Rank 7 - Lang mixed
Q: Article 19A mein public importance ki information ka kya haq hai?

Gold: PAKISTANCODE__Constitution_of_Pakistan__2026-09-26__EN__Under_Review.pdf p31
Got Top1: PAKISTANCODE__ESTACODE_2021__2026-09-27__EN__Official.txt
Gold answer snippet: Every citizen shall have the right to have access to information in all matters of public importance subject to regulation and reasonable restrictions imposed by law.

Hypothesis: BM25 matched wrong article number, dense missed numeric signal

---

