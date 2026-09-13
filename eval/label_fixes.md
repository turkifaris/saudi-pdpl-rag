# Label corrections

Two gold labels were incomplete. Each correction is justified by quoting the
article text, not by what the system returned. Metrics before and after are
both reported in `results.md`.

| Question | Before | After | Evidence from the article |
|---|---|---|---|
| q080 «متى يقدرون يرفضون طلبي إني أشوف بياناتي؟» | [5] | [3, 5] | Art. 3: «يكون لجهة التحكم عدم الاستجابة للطلب، على أن يكون ذلك مسبباً» — the general provision governing refusal of any rights request. Art. 5 covers a different ground (third-party rights, trade secrets). Both apply. |
| q028 «أخذوا بياناتي من طرف ثالث بدون ما أدري، جايز كذا؟» | [15] | [4, 15] | Art. 4: «في حال تم جمع البيانات من غير صاحبها مباشرة... خلال مدة لا تتجاوز 30 يوماً اتخاذ الخطوات اللازمة لإبلاغ صاحب البيانات» — the «without my knowledge» half of the question is Art. 4; the permissibility half is Art. 15. |

## Reviewed and left unchanged
| Question | Label | Why it stands |
|---|---|---|
| q027 | [22] | Art. 22(ج): «إشعار الجهات التي أُفصح لها عن البيانات الشخصية» answers the question literally. Genuine retrieval failure (top-1 score 0.009). |
| q037 | [12] | Art. 12: «اتخاذ الإجراءات الملائمة لإشعار من تم الإفصاح لهم... وطلب إتلافها» answers it literally. Genuine retrieval failure (top-1 score 0.005). |

Both genuine failures score near zero, so the rejection threshold suppresses
them — the system abstains rather than answering wrongly.
