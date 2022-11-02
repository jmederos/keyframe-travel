import os
import gradio as gr
import numpy as np
import modules.scripts as scripts
import modules.shared as shared
from modules.processing import Processed, process_images

class Script(scripts.Script):
    def title(self):
        return 'Keyframe Travel'

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        show_images = gr.Checkbox(label='Display generated frames', value=False)
        save_video = gr.Checkbox(label='Save video', value=True)
        video_fps = gr.Number(label='Video FPS', value=5)
        interpolation_steps = gr.Number(label='Interpolation frames', value=0)

        if is_img2img:
            keyframes = gr.Dataframe(label='Keyframes', headers=['steps', 'cfg_scale', 'denoising_strength'], type="numpy", datatype="number", row_count=2, col_count=(3, 'fixed'))
        else:
            keyframes = gr.Dataframe(label='Keyframes', headers=['steps', 'cfg_scale'], type='numpy', datatype="number", row_count=2, col_count=(2, 'fixed'))
        return [keyframes, interpolation_steps, save_video, video_fps, show_images]

    def get_next_sequence_number(path):
        from pathlib import Path
        """
        Determines and returns the next sequence number to use when saving an image in the specified directory.
        The sequence starts at 0.
        """
        result = -1
        dir = Path(path)
        for file in dir.iterdir():
            if not file.is_dir(): continue
            try:
                num = int(file.name)
                if num > result: result = num
            except ValueError:
                pass
        return result + 1

    def interpolate_frames(keyframes, interpolation_steps):
        # Create a new array matching the number of columns
        keyframes_shape = keyframes.shape[1]
        interpolated_frames = np.empty((0, keyframes_shape))
        keyframes_requested = keyframes.shape[0]

        for frame_index in range(keyframes_requested - 1):
            steps_interp = np.linspace(
                int(keyframes[frame_index][0]), int(keyframes[frame_index + 1][0]), interpolation_steps + 1, # Need to cast, gradio passes float and np complains, similar elsewhere
                endpoint=False, dtype=int
                )
            cfg_interp = np.linspace(
                float(keyframes[frame_index][1]), float(keyframes[frame_index + 1][1]), interpolation_steps + 1,
                endpoint=False, dtype=float
                )
            if keyframes_shape > 2:          # If we have 3 parameters to interpolate
                denoise_interp = np.linspace(
                float(keyframes[frame_index][2]), float(keyframes[frame_index + 1][2]), interpolation_steps + 1,
                endpoint=False, dtype=float
                )
                cur_interp = np.column_stack((steps_interp, cfg_interp, denoise_interp))
            else:
                cur_interp = np.column_stack((steps_interp, cfg_interp))

            interpolated_frames = np.concatenate((interpolated_frames, cur_interp), axis=0)

        # Ensure last keyframe is loaded
        interpolated_frames = np.vstack((interpolated_frames, keyframes[-1]))
        return interpolated_frames

    def run(self, p, keyframes, interpolation_steps, save_video, video_fps, show_images):
        initial_info = None
        images = []

        keyframes_shape = keyframes.shape[1]
        keyframes_requested = keyframes.shape[0]
        total_num_frames = 0
        total_num_steps  = 0
        interp_frames_requested = int(interpolation_steps)
        frames_to_generate = None

        # Force Batch Count and Batch Size to 1.
        p.n_iter = 1
        p.batch_size = 1

        # Custom travel saving
        travel_path = os.path.join(p.outpath_samples, "kf-travels")
        os.makedirs(travel_path, exist_ok=True)
        travel_number = Script.get_next_sequence_number(travel_path)
        travel_path = os.path.join(travel_path, f"{travel_number:05}")
        p.outpath_samples = travel_path

        if keyframes_requested < 1:
            print(f"You need at least 1 keyframe")
            return Processed(p, images, p.seed)

        if save_video and not show_images:
            print(f"Nothing to show in GUI. You will find the result in the output folder.")

        if save_video:
            try:
                import moviepy.video.io.ImageSequenceClip as ImageSequenceClip
            except ImportError:
                print(f"moviepy not installed; cannot generate video")
                return Processed(p, images, p.seed)

        if interp_frames_requested < 1:
            frames_to_generate = keyframes                                                          # No interpolation requested
        else:
            frames_to_generate = Script.interpolate_frames(keyframes, interp_frames_requested)      # Interpolation requested
        
        total_num_frames = frames_to_generate.shape[0]
        total_num_steps  = int(frames_to_generate.sum(axis=0, dtype=float)[0])
        print(f"Keyframe Travel will create {total_num_frames} frames. Total steps to process: {total_num_steps}")
        # TODO: Save frames_to_generate as CSV receipt 🤔

        # Set generation helpers
        shared.state.job_count = total_num_frames
        shared.total_tqdm.updateTotal(total_num_steps)

        for frame in frames_to_generate:
            if shared.state.interrupted:
                break
 
            p.steps     = int(float(frame[0]))
            p.cfg_scale = float(frame[1])
            p.sd_model  = shared.sd_model

            if keyframes_shape > 2:
                p.denoising_strength = float(frame[2])

            proc = process_images(p)

            if initial_info is None:
                initial_info = proc.info
            
            images += proc.images

        if save_video:
            print(f"Keyframe Travel generating video...")
            clip = ImageSequenceClip.ImageSequenceClip([np.asarray(t) for t in images], fps=video_fps)
            clip.write_videofile(os.path.join(travel_path, f"kf-travel-{travel_number:05}.mp4"), verbose=False, logger=None)

        processed = Processed(p, images if show_images else [], p.seed, initial_info)
        return processed

    def describe(self):
        return "Travel between keyframes differing in Steps, CFG, and/or Denoising"
