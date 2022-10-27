# Keyframe Travel
Script for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) to generate images using keyframes.

Based on [yownas/seed_travel](https://github.com/yownas/seed_travel).

## Usage
### Installation
1. Copy `keyframe_travel.py` to `stable-diffusion-webui/scripts`
2. Optionally, install `moviepy` if video output is desired

### Options/Parameters
`Display generated frames`: Shows all generated frames in the output section; not recommended for large image sets.
`Save video`: Save generated frames as an `*.mp4`
`Video FPS`: Frames per second value for output video.
`Interpolation frames`: Number of frames to generate between keyframes.

### Keyframes
Each row represents a keyframe to generate
#### `txt2img`
`steps` and `cfg_scale` can be assigned to each keyframe
#### `img2img`
`steps`, `cfg_scale`, and `denoising_strength` can be assigned to each keyframe

### Output
The frames/video will output to a `kf-travels` subfolder of the output folder of the respective generation mode `txt2img` or `img2img`

## `img2img` Example

#### Prompt
`(painting of a lion) by Pablo Picasso, cubist masterpiece`

#### Negative Prompt
`lowres, jpeg artifacts, low quality`

#### Seed
`1245514267`

#### Source Image
![cat](https://pixnio.com/free-images/custom-size/pixnio-2723120-512.jpg)
_[Sample image licensed under CC0](https://pixnio.com/media/black-and-white-domestic-cat-eyes-orange-yellow-portrait)_

#### Keyframe Travel
```
Display generated frames: false
Save video: true
Video FPS: 5
Interpolation frames: 5
```
| `steps` | `cfg_scale` | `denoising_strength` |
|:-------:|:-----------:|:--------------------:|
|    30   |      2      |           0          |
|    30   |      5      |         0.25         |
|    30   |      8      |          0.5         |
|    30   |      9      |          0.7         |
|    30   |      10     |          0.8         |

### Output
![frame-05](example/00005-1245514267-(painting%20of%20a%20lion)%20by%20Pablo%20Picasso%2C%20cubist%20masterpiece.png)
![frame-10](example/00010-1245514267-(painting%20of%20a%20lion)%20by%20Pablo%20Picasso%2C%20cubist%20masterpiece.png)
![frame-20](example/00020-1245514267-(painting%20of%20a%20lion)%20by%20Pablo%20Picasso%2C%20cubist%20masterpiece.png)

## [Download Animation](example/kf-travel-00000.mp4)
