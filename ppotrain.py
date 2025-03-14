import gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.monitor import Monitor
import numpy as np
import os
import torch


class MarchMadnessEnv(gym.Env):
    def __init__(self):
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(129,), dtype=np.float32
        )
        self.action_space = gym.spaces.Discrete(5)

    def reset(self):
        observation = []
        return observation

    def step(self, action):
        observation, reward, done, info = [], 0, False, []
        return observation, reward, done, info

def make_env(env):
    def _init():
        return MarchMadnessEnv()

    return _init


def ppotrain(env, total_timesteps=1000000, save_path="./models/march_madness_model"):
    # Create log dir
    log_dir = "logs/"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs("./models", exist_ok=True)

    # Vectorize and normalize environment
    env = DummyVecEnv([lambda: env])
    env = VecNormalize(env,
                       norm_obs=True,
                       norm_reward=True,
                       clip_obs=10.,
                       clip_reward=10.)

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
        learning_rate=3e-4,
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
                pi=[256, 256],
                vf=[256, 256]
            ),
            activation_fn=torch.nn.ReLU
        ),
        verbose=1
    )

    # Train the model
    model.learn(
        total_timesteps=total_timesteps,
        callback=save_callback
    )

    # Save the final model
    model.save(f"{save_path}/final_model")
    env.save(f"{save_path}/vec_normalize.pkl")

    return model, env


def load_trained_model(env, path="./models/march_madness_model"):
    """
    Load a trained model and the normalized environment
    """
    # Load the saved statistics
    env = DummyVecEnv([lambda: env])
    env = VecNormalize.load(f"{path}/vec_normalize.pkl", env)
    # Do not update them at test time
    env.training = False
    # Do not normalize reward at test time
    env.norm_reward = False

    # Load the model
    model = PPO.load(f"{path}/final_model", env=env)

    return model, env


def evaluate_model(model, env, num_episodes=100):
    """
    Evaluate the trained model
    """
    rewards = []
    for episode in range(num_episodes):
        obs = env.reset()
        episode_reward = 0
        done = False

        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward

        rewards.append(episode_reward)

        if episode % 10 == 0:
            print(f"Episode {episode}: Reward = {episode_reward}")

    mean_reward = np.mean(rewards)
    std_reward = np.std(rewards)
    print(f"\nMean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

    return mean_reward, std_reward


# Example usage:
if __name__ == "__main__":

    # Our environment
    env = MarchMadnessEnv()

    # Train the model
    model, trained_env = ppotrain(env, total_timesteps=1000000)

    # Loading trained model
    print("Loading trained model...")
    env_for_eval = MarchMadnessEnv()  # Create fresh environment for evaluation
    loaded_model, loaded_env = load_trained_model(env_for_eval)

    # Evaluation
    print("Evaluating model...")
    evaluate_model(loaded_model, loaded_env)
