"""
🔵
├── embeddings(BertEmbeddings)
│   ├── word_embeddings(Embedding) weight[30522, 768]
│   ├── position_embeddings(Embedding) weight[512, 768]
│   ├── token_type_embeddings(Embedding) weight[2, 768]
│   └── LayerNorm(LayerNorm) weight[768] bias[768]
├── encoder(BertEncoder)
│   └── layer(ModuleList)
│       └── +0-11(BertLayer)
│           ├── attention(BertAttention)
│           │   ├── self(BertSelfAttention)
│           │   │   └── +query,key,value(Linear) weight[768, 768] bias[768]
│           │   └── output(BertSelfOutput)
│           │       ├── dense(Linear) weight[768, 768] bias[768]
│           │       └── LayerNorm(LayerNorm) weight[768] bias[768]
│           ├── intermediate(BertIntermediate)
│           │   └── dense(Linear) weight[3072, 768] bias[3072]
│           └── output(BertOutput)
│               ├── dense(Linear) weight[768, 3072] bias[768]
│               └── LayerNorm(LayerNorm) weight[768] bias[768]
└── pooler(BertPooler)
    └── dense(Linear) weight[768, 768] bias[768]
********************************************************************************
🔵
├── embeddings(BertEmbeddings)
│   ├── word_embeddings(Embedding) weight[30522, 768](cuda:0)
│   ├── position_embeddings(Embedding) weight[512, 768](cuda:0)
│   ├── token_type_embeddings(Embedding) weight[2, 768](cuda:0)
│   └── LayerNorm(LayerNorm) weight[768](cuda:0) bias[768](cuda:0)
├── encoder(BertEncoder)
│   └── layer(ModuleList)
│       ├── 0(BertLayer)
│       │   ├── attention(BertAttention)
│       │   │   ├── self(BertSelfAttention)
│       │   │   │   ├── query(Linear) weight[768, 768](cuda:0)❄️  bias[768](cuda:0)
│       │   │   │   └── +key,value(Linear) weight[768, 768](cuda:0) bias[768](cuda:0)
│       │   │   └── output(BertSelfOutput)
│       │   │       ├── dense(Linear) weight[768, 768](cuda:0) bias[768](cuda:0)
│       │   │       └── LayerNorm(LayerNorm) weight[768](cuda:0) bias[768](cuda:0)
│       │   ├── intermediate(BertIntermediate)
│       │   │   └── dense(Linear) weight[3072, 768](cuda:0) bias[3072](cuda:0)
│       │   └── output(BertOutput)
│       │       ├── dense(Linear) weight[768, 3072](cuda:0) bias[768](cuda:0)
│       │       └── LayerNorm(LayerNorm) weight[768](cuda:0) bias[768](cuda:0)
│       └── +1-11(BertLayer)
│           ├── attention(BertAttention)
│           │   ├── self(BertSelfAttention)
│           │   │   └── +query,key,value(Linear) weight[768, 768](cuda:0) bias[768](cuda:0)
│           │   └── output(BertSelfOutput)
│           │       ├── dense(Linear) weight[768, 768](cuda:0) bias[768](cuda:0)
│           │       └── LayerNorm(LayerNorm) weight[768](cuda:0) bias[768](cuda:0)
│           ├── intermediate(BertIntermediate)
│           │   └── dense(Linear) weight[3072, 768](cuda:0) bias[3072](cuda:0)
│           └── output(BertOutput)
│               ├── dense(Linear) weight[768, 3072](cuda:0) bias[768](cuda:0)
│               └── LayerNorm(LayerNorm) weight[768](cuda:0) bias[768](cuda:0)
└── pooler(BertPooler)
    └── dense(Linear) weight[768, 768](cuda:0) bias[768](cuda:0)
"""

from transformers import BertModel
from hiq.vis import print_model

model = BertModel.from_pretrained("bert-base-uncased")

print_model(model)

print("*" * 80)
model.embeddings.word_embeddings.requires_grad = False
model.encoder.layer[0].attention.self.query.weight.requires_grad = False
model = model.cuda()
print_model(model)
