import json
import torch


def read_config():
    with open("./config/config.json", "r", encoding="utf-8") as f:
        data = f.read()
        config = json.loads(data)
        return config


def set_cuda_device(process):
    count = torch.cuda.device_count()
    device = process % count
    torch.cuda.set_device(device)


def get_cuda_info():
    gpu_ids = []
    if torch.cuda.is_available():
        gpu_ids += [gpu_id for gpu_id in range(torch.cuda.device_count())]
        result = {
            "available": torch.cuda.is_available(),
            "count": torch.cuda.device_count(),
            "current": torch.cuda.current_device(),
            "gpus": gpu_ids
        }
    else:
        result = {
            "available": False,
            "count": 0,
            "current": 0,
            "gpus": []
        }

    return result
