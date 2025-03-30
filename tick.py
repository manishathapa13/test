import streamlit as st
import numpy as np
import random
import pickle
import os

# --------------------- Tic-Tac-Toe Game ---------------------
class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_winner = None

    def reset(self):
        self.board = [' '] * 9
        self.current_winner = None
        return self.get_state()

    def get_state(self):
        return tuple(self.board)

    def available_actions(self):
        return [i for i, x in enumerate(self.board) if x == ' ']

    def make_move(self, action, player):
        if self.board[action] == ' ':
            self.board[action] = player
            if self.check_winner(player):
                self.current_winner = player
            return True
        return False

    def check_winner(self, player):
        win_patterns = [(0,1,2), (3,4,5), (6,7,8),
                        (0,3,6), (1,4,7), (2,5,8),
                        (0,4,8), (2,4,6)]
        return any(all(self.board[i] == player for i in pattern) for pattern in win_patterns)

    def is_full(self):
        return ' ' not in self.board

# --------------------- Q-Learning Agent ---------------------
class QLearningAgent:
    def __init__(self, player='O', alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}
        self.player = player
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.load_q_table()

    def load_q_table(self):
        if os.path.exists("q_table.pkl"):
            with open("q_table.pkl", "rb") as f:
                self.q_table = pickle.load(f)

    def save_q_table(self):
        with open("q_table.pkl", "wb") as f:
            pickle.dump(self.q_table, f)

    def get_qs(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0] * 9
        return self.q_table[state]

    def choose_action(self, state, available_actions, train=False):
        if train and random.random() < self.epsilon:
            return random.choice(available_actions)
        qs = self.get_qs(state)
        best = max([qs[a] if a in available_actions else -float('inf') for a in range(9)])
        best_actions = [a for a in available_actions if qs[a] == best]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done):
        qs = self.get_qs(state)
        next_qs = self.get_qs(next_state)
        if done:
            target = reward
        else:
            target = reward + self.gamma * max(next_qs)
        qs[action] += self.alpha * (target - qs[action])

# --------------------- Streamlit App ---------------------
st.title("🧠 Tic-Tac-Toe with Q-Learning")
st.markdown("You are **❌ (X)** | AI is **⭕ (O)**")

# Load or initialize game/agent
if 'game' not in st.session_state:
    st.session_state.game = TicTacToe()
    st.session_state.board = st.session_state.game.board.copy()
    st.session_state.agent = QLearningAgent()
    st.session_state.train_mode = False

game = st.session_state.game
agent = st.session_state.agent
game.board = st.session_state.board

# Toggle Train Mode
st.sidebar.title("⚙️ Settings")
st.session_state.train_mode = st.sidebar.checkbox("Training Mode", value=False)
if st.sidebar.button("💾 Save Q-Table"):
    agent.save_q_table()
    st.sidebar.success("Q-Table saved.")
if st.sidebar.button("🧽 Reset Q-Table"):
    agent.q_table = {}
    st.sidebar.warning("Q-Table reset.")

# Game Grid
cols = st.columns(3)
for i in range(9):
    with cols[i % 3]:
        if game.board[i] == ' ' and game.current_winner is None:
            if st.button(" ", key=i):
                game.make_move(i, 'X')
                state = game.get_state()
                if not game.current_winner and not game.is_full():
                    action = agent.choose_action(state, game.available_actions(), train=st.session_state.train_mode)
                    game.make_move(action, 'O')
                    next_state = game.get_state()
                    reward = 1 if game.current_winner == 'O' else 0
                    agent.update(state, action, reward, next_state, game.current_winner is not None or game.is_full())
                st.session_state.board = game.board.copy()
                st.rerun()
        else:
            st.markdown(f"<div style='text-align:center; font-size:30px'><b>{game.board[i]}</b></div>", unsafe_allow_html=True)

# Game Status
if game.current_winner:
    st.success(f"🎉 Player **{game.current_winner}** wins!")
elif game.is_full():
    st.warning("🤝 It's a draw!")

# Restart
if st.button("🔄 Restart Game"):
    st.session_state.game = TicTacToe()
    st.session_state.board = [' '] * 9
    st.rerun()
