# Jax-Volumetric-Renderer
A Jax based renderer for plenoxels, work in progress...

![Screenshot from 2023-11-16 13-32-49](https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/5a6c8778-d64f-4852-8280-39b1cee3e350)

![img_c1_slim](https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/16f4c186-9292-4215-a78c-ea03be6ccd33)

This is an ongoing project on Plenoxels, for didactic purposes, from this paper: https://alexyu.net/plenoxels/

I am attempting to make a fast renderer in Jax, but using only a 8gb GPU. The full models as are 512x512x512, but we render only
128x128x128, more is possible but requires more batching and potentially some other tricks like voxel partitionning. 

Other small things I've done to make things fit in memory:
- Work in float16
- Render one channel at a time
- Find the silhouette of the model to be rendered

Things I've tried but did not work out:
- Used Octrees, they just don't work with Jax due to memory coalescence.

Need to download the model weights from here: 
https://drive.google.com/drive/folders/128yBriW1IG_3NJ5Rp7APSTZsJqdJdfc1

To have all the requirements installed, you need:
- Jax
- Opencv
- Numpy
- Open3d

Tips to install Jax:
- Follow the steps on the website: https://jax.readthedocs.io/en/latest/installation.html
- If you work in Pycharm, first launch the virtual env from the terminal, then launch Pycharm from the same terminal
- If you call both TF2 or Torch as you call Jax (or even import them) you will likely run out of memory. They don't like each other.

TODO: 
- Provide install script
- Make python install wheel
- Work on the optimization/training steps
- Get a GPU with more VRAM
