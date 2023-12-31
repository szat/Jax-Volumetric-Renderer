# Jax-Volumetric-Renderer
A Jax based renderer for plenoxels, work in progress...

<p>
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/5a6c8778-d64f-4852-8280-39b1cee3e350"
 width="300" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/16f4c186-9292-4215-a78c-ea03be6ccd33"
 width="200" height="200" />
    <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/78dc14d3-1902-4c0f-9b2a-d1d9568659cf"
 width="200" height="200" />
  
This is an ongoing project on Plenoxels, for didactic purposes, from this paper: https://alexyu.net/plenoxels/

I am attempting to make a fast renderer in Jax, but using only a 8gb GPU. The full models as are 512x512x512, but we render only
128x128x128, more is possible but requires more batching and potentially some other tricks like voxel partitionning. 

## Usage:
- The main work loop is in renderer_script.py, you will have to replace the relative paths so that the script can find the weights to the model.
- The best is to run in the interpreter, there are a few calls to Open3d just to visualize what is happening, but actually not necessary.
- The end result is in the end in an image buffer. 

## Other small things I've done to make things fit in memory:
- Work in float16
- Render one channel at a time
- Find the silhouette of the model to be rendered

## Things I've tried but did not work out:
- Used Octrees, they just don't work with Jax due to memory coalescence.

Need to download the model weights from here: 
https://drive.google.com/drive/folders/128yBriW1IG_3NJ5Rp7APSTZsJqdJdfc1

## To have all the requirements installed, you need:
- Jax
- Opencv
- Numpy
- Open3d, just to visualize some stuff. 

## Tips to install Jax:
- Follow the steps on the website: https://jax.readthedocs.io/en/latest/installation.html
- If you work in Pycharm, first launch the virtual env from the terminal, then launch Pycharm from the same terminal
- If you call both TF2 or Torch as you call Jax (or even import them) you will likely run out of memory. They don't like each other.

## TODO: 
- Figure out where the random black dots are coming from on the render
- Provide install script
- Make python install wheel
- Work on the optimization/training steps
- Get a GPU with more VRAM

## Bloopers:
  
<p>
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/bb131ec4-68b6-4b45-a08e-65b68a22c5b9"
 width="200" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/a9614103-b6e9-42af-927c-d9e281cd85c6"
 width="200" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/99521272-81b3-4155-92e4-81ff14ede436"
 width="200" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/d3e98ddc-608a-4020-9be9-095ee28f54f0"
 width="200" height="200" />
    </p>

<p>
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/acc4034c-0e94-4870-819c-ebcfc9857b5a"
 width="200" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/49772b83-79c4-439d-b865-a2a6731b549d"
 width="200" height="200" />
    <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/acbae107-d3cb-4b41-bf59-d23b428a3edd"
 width="200" height="200" />
  <img src="https://github.com/szat/Jax-Volumetric-Renderer/assets/5555551/972565ad-d358-4359-a2e5-160ee6ef6a96"
 width="200" height="200" />
</p>
