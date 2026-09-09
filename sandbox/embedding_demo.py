from sentence_transformers import SentenceTransformer, util
import torch

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"الجهاز المستخدم: {device}\n")

model = SentenceTransformer("intfloat/multilingual-e5-small", device=device)

جمل = [
    "يجب الحصول على موافقة صاحب البيانات قبل جمعها",
    "لا يجوز جمع البيانات الشخصية دون موافقة صاحبها",
    "تبدأ مواعيد العمل الرسمية الساعة الثامنة صباحاً",
]

متجهات = model.encode(جمل)
print("شكل المصفوفة:", متجهات.shape, "\n")

تشابه = util.cos_sim(متجهات, متجهات)
for i in range(len(جمل)):
    for j in range(i + 1, len(جمل)):
        print(f"({i+1}) ↔ ({j+1}) : {تشابه[i][j]:.3f}")
