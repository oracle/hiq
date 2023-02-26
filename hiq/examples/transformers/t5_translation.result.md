```
$python t5_translation_driver.py 
Bonjour, comment êtes-vous ?
[2023-02-25 23:38:38.089010 - 23:38:47.674455]  [100.00%] 🟢_root_time(9.5854)
                                                            [OH:51596us]
[2023-02-25 23:38:38.089010 - 23:38:38.193248]  [  1.09%]    |___from_pretrained(0.1042) ({'args': 'str(t5-small)', 'kwargs': "{'device': 'str(cuda)'}"})
[2023-02-25 23:38:42.864306 - 23:38:42.890623]  [  0.27%]    |___from_pretrained(0.0263) ({'args': 'str(t5-small)', 'kwargs': "{'return_unused_kwargs': 'bool(True)', 'trust_remote_code': 'None', 'revision': 'None', 'use_auth_token': 'None', '_commit_hash': 'None', '_from_pipeline': 'str(text2text-generation)', '_from_auto': 'bool(True)'}"})
[2023-02-25 23:38:42.898707 - 23:38:43.093866]  [  2.04%]    |___torch_load(0.1952) ({'args': 'str(/home/wfh/.cache/huggingface/hub/models--t5-small/snapshots/3479082dc36f8a4730936ef1c9b88cd8b0835c53)...', 'kwargs': "{'map_location': 'str(cpu)'}"})
[2023-02-25 23:38:44.158301 - 23:38:44.160066]  [  0.02%]    |___from_pretrained(0.0018) ({'args': 'str(t5-small)', 'kwargs': "{'trust_remote_code': 'None', '_from_pipeline': 'str(text2text-generation)', 'revision': 'None', 'use_auth_token': 'None', '_commit_hash': 'str(3479082dc36f8a4730936ef1c9b88cd8b0835c53)', '_from_auto': 'bool(True)'}"})
[2023-02-25 23:38:44.161243 - 23:38:44.162715]  [  0.02%]    |___from_pretrained(0.0015) ({'args': 'str(t5-small)', 'kwargs': "{'use_auth_token': 'None', 'cache_dir': 'None', 'local_files_only': 'bool(False)', '_commit_hash': 'str(3479082dc36f8a4730936ef1c9b88cd8b0835c53)'}"})
[2023-02-25 23:38:46.853896 - 23:38:47.674455]  [  8.56%]    l___pp_call(0.8206) ({'args': 'Text2TextGenerationPipeline(<transformers.pipelines.text2text_generation.Text2TextGenerationPipeline object at 0x7fe87e980850>),str(translate English to French: Hello, how are you?)', 'kwargs': "{'max_length': 'int(50)'}"})

                                                [2664.000 - 2844.000]  [100.00%] 🟢_root_total_gpu_memory_mb_nvml(180.0000)
[2023-02-25 23:38:46.853936 - 23:38:47.674485]  [2664.000 - 2844.000]  [100.00%]    l___pp_call(180.0000) ({'args': 'Text2TextGenerationPipeline(<transformers.pipelines.text2text_generation.Text2TextGenerationPipeline object at 0x7fe87e980850>),str(translate English to French: Hello, how are you?)', 'kwargs': "{'max_length': 'int(50)'}"})
```
