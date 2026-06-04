python -c "
import torch
print('\n--- System Diagnostics ---')
print(f'PyTorch Version: {torch.__version__}')
print(f'CUDA Available:  {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version:    {torch.version.cuda}')
    print(f'GPU Detected:    {torch.cuda.get_device_name(0)}')
else:
    print('WARNING: PyTorch cannot see your GPU!')
print('--------------------------\n')
"
