from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

import os
import torch

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.vec_env import VecCheckNan

def linear_schedule(initial_value):
    def schedule(progress):
        return initial_value * (1 - progress)
    return schedule

def ppotrain(env, total_timesteps=2000000, save_path="./models/march_madness_model"):
    # Create log dir
    log_dir = "logs/"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs("./models", exist_ok=True)

    # Vectorize and normalize environment
    env = DummyVecEnv([lambda: env])
    env = VecCheckNan(env)  # Check for NaN values
    env = VecNormalize(
        env,
        norm_obs=True,
        norm_reward=True,
        clip_obs=10.,
        clip_reward=10.,
        gamma=0.99
    )

    # Create callback for saving best model
    save_callback = EvalCallback(env,
                                 best_model_save_path=save_path,
                                 log_path=log_dir,
                                 eval_freq=10000,
                                 deterministic=True,
                                 render=False,
                                 n_eval_episodes=5)

    # Initialize PPO model with optimized hyperparameters
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=linear_schedule(3e-4),
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        clip_range_vf=0.2,
        ent_coef=0.0,
        vf_coef=0.5,
        max_grad_norm=0.5,
        use_sde=False,
        sde_sample_freq=-1,
        target_kl=None,
        tensorboard_log=log_dir,
        policy_kwargs=dict(
            net_arch=dict(
                pi=[512, 256, 128],  # Larger policy network
                vf=[512, 256, 128]  # Larger value network
            ),
            activation_fn=torch.nn.ReLU
        ),
        verbose=1
    )

    # Training loop
    observation = env.reset()
    for t in range(total_timesteps):
        # Get action from model
        action, _states = model.predict(observation, deterministic=False)

        # Execute action in environment
        next_observation, reward, done, info = env.step(action)

        checkpoint_callback = CheckpointCallback(
            save_freq=10000,
            save_path="./checkpoints/",
            name_prefix="march_madness_model"
        )

        # Combine callbacks
        callbacks = [save_callback, checkpoint_callback]

        model.learn(
            total_timesteps=total_timesteps,
            callback=save_callback
        )

        # Update observation
        observation = next_observation

        if done:
            observation = env.reset()

        if t % 1000 == 0:
            print(f"Step {t}/{total_timesteps}")

    return model


if __name__ == "__main__":
    teams_df = pd.DataFrame()

    historical_df = pd.DataFrame()

    # 2. Create the environment
    env = MarchMadnessEnv(
        teams_df=teams_df,
        historical_df=historical_df,
        num_entries=5  # Number of entries per participant
    )

    # Create and wrap environment
    env = MarchMadnessEnv(teams_df=teams_df, historical_df=historical_df)
    env = DummyVecEnv([lambda: env])

    # Train model
    model = ppotrain(env)

    # Save trained model
    model.save("march_madness_model")
