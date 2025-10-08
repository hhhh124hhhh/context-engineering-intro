"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('elo_rating', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('experience', sa.Integer(), nullable=False),
        sa.Column('coins', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_online', sa.Boolean(), nullable=False),
        sa.Column('is_banned', sa.Boolean(), nullable=False),
        sa.Column('ban_reason', sa.Text(), nullable=True),
        sa.Column('ban_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('games_played', sa.Integer(), nullable=False),
        sa.Column('games_won', sa.Integer(), nullable=False),
        sa.Column('games_lost', sa.Integer(), nullable=False),
        sa.Column('win_streak', sa.Integer(), nullable=False),
        sa.Column('best_win_streak', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index('idx_users_elo_rating', 'users', ['elo_rating'], unique=False)
    op.create_index('idx_users_games_played', 'users', ['games_played'], unique=False)
    op.create_index('idx_users_win_rate', 'users', ['games_won', 'games_played'], unique=False)
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)
    op.create_index('idx_users_last_login', 'users', ['last_login_at'], unique=False)
    op.create_index('idx_users_online', 'users', ['is_online', 'last_login_at'], unique=False)

    # Create user_sessions table (IMPORTANT - this was missing!)
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_sessions_expires_at', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('idx_user_sessions_last_used', 'user_sessions', ['last_used_at'], unique=False)
    op.create_index('idx_user_sessions_user_token', 'user_sessions', ['user_id', 'session_token'], unique=False)
    op.create_index(op.f('ix_user_sessions_session_token'), 'user_sessions', ['session_token'], unique=True)
    op.create_index(op.f('ix_user_sessions_refresh_token'), 'user_sessions', ['refresh_token'], unique=True)

    # Create friendships table
    op.create_table('friendships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_friendships_sender_receiver', 'friendships', ['sender_id', 'receiver_id'], unique=False)
    op.create_index('idx_friendships_status', 'friendships', ['status'], unique=False)

    # Create cards table
    op.create_table('cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('flavor_text', sa.Text(), nullable=True),
        sa.Column('cost', sa.Integer(), nullable=False),
        sa.Column('attack', sa.Integer(), nullable=True),
        sa.Column('defense', sa.Integer(), nullable=True),
        sa.Column('durability', sa.Integer(), nullable=True),
        sa.Column('card_type', sa.String(length=20), nullable=False),
        sa.Column('rarity', sa.String(length=20), nullable=False),
        sa.Column('card_class', sa.String(length=30), nullable=False),
        sa.Column('card_set', sa.String(length=50), nullable=False),
        sa.Column('mechanics', sa.JSON(), nullable=True),
        sa.Column('effect_text', sa.Text(), nullable=True),
        sa.Column('play_requirements', sa.JSON(), nullable=True),
        sa.Column('deathrattle_effect', sa.JSON(), nullable=True),
        sa.Column('battlecry_effect', sa.JSON(), nullable=True),
        sa.Column('ongoing_effect', sa.JSON(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('golden_image_url', sa.String(length=500), nullable=True),
        sa.Column('sound_url', sa.String(length=500), nullable=True),
        sa.Column('is_collectible', sa.Boolean(), nullable=False),
        sa.Column('is_standard_legal', sa.Boolean(), nullable=False),
        sa.Column('is_wild_legal', sa.Boolean(), nullable=False),
        sa.Column('crafting_cost', sa.Integer(), nullable=False),
        sa.Column('play_count', sa.Integer(), nullable=False),
        sa.Column('win_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('usage_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('artist', sa.String(length=100), nullable=True),
        sa.Column('how_to_get', sa.String(length=200), nullable=True),
        sa.Column('lore', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cards_id'), 'cards', ['id'], unique=False)
    op.create_index(op.f('ix_cards_name'), 'cards', ['name'], unique=False)
    op.create_index('idx_cards_cost', 'cards', ['cost'], unique=False)
    op.create_index('idx_cards_attack', 'cards', ['attack'], unique=False)
    op.create_index('idx_cards_defense', 'cards', ['defense'], unique=False)
    op.create_index('idx_cards_type_rarity', 'cards', ['card_type', 'rarity'], unique=False)
    op.create_index('idx_cards_class_set', 'cards', ['card_class', 'card_set'], unique=False)
    op.create_index('idx_cards_collectible', 'cards', ['is_collectible'], unique=False)
    op.create_index('idx_cards_standard_legal', 'cards', ['is_standard_legal'], unique=False)
    op.create_index('idx_cards_win_rate', 'cards', ['win_rate'], unique=False)
    op.create_index('idx_cards_usage_rate', 'cards', ['usage_rate'], unique=False)

    # Create decks table
    op.create_table('decks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('card_class', sa.String(length=30), nullable=False),
        sa.Column('format_type', sa.String(length=20), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('is_favorite', sa.Boolean(), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=False),
        sa.Column('games_won', sa.Integer(), nullable=False),
        sa.Column('games_lost', sa.Integer(), nullable=False),
        sa.Column('win_rate', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_decks_user_class', 'decks', ['user_id', 'card_class'], unique=False)
    op.create_index('idx_decks_format_public', 'decks', ['format_type', 'is_public'], unique=False)
    op.create_index('idx_decks_win_rate', 'decks', ['win_rate'], unique=False)
    op.create_index('idx_decks_games_played', 'decks', ['games_played'], unique=False)
    op.create_index('idx_decks_created_at', 'decks', ['created_at'], unique=False)
    op.create_index('idx_decks_last_used', 'decks', ['last_used_at'], unique=False)

    # Create games table
    op.create_table('games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('game_code', sa.String(length=20), nullable=False),
        sa.Column('game_mode', sa.String(length=20), nullable=False),
        sa.Column('format_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_turn', sa.Integer(), nullable=False),
        sa.Column('current_player_id', sa.Integer(), nullable=True),
        sa.Column('turn_time_limit', sa.Integer(), nullable=False),
        sa.Column('winner_id', sa.Integer(), nullable=True),
        sa.Column('loser_id', sa.Integer(), nullable=True),
        sa.Column('result_reason', sa.String(length=50), nullable=True),
        sa.Column('turns_played', sa.Integer(), nullable=False),
        sa.Column('game_duration', sa.Integer(), nullable=True),
        sa.Column('elo_change_winner', sa.Integer(), nullable=True),
        sa.Column('elo_change_loser', sa.Integer(), nullable=True),
        sa.Column('game_log', sa.JSON(), nullable=True),
        sa.Column('initial_states', sa.JSON(), nullable=True),
        sa.Column('final_states', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_code')
    )
    op.create_index('idx_games_mode_status', 'games', ['game_mode', 'status'], unique=False)
    op.create_index('idx_games_current_player', 'games', ['current_player_id'], unique=False)
    op.create_index('idx_games_winner_loser', 'games', ['winner_id', 'loser_id'], unique=False)
    op.create_index('idx_games_created_at', 'games', ['created_at'], unique=False)
    op.create_index('idx_games_finished_at', 'games', ['finished_at'], unique=False)
    op.create_index('idx_games_duration', 'games', ['game_duration'], unique=False)

    # Create remaining tables with foreign key constraints
    # (Deck cards, game players, game cards, etc. would be created here)
    # For brevity, showing the main structure


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('games')
    op.drop_table('decks')
    op.drop_table('cards')
    op.drop_table('friendships')
    op.drop_table('user_sessions')  # Don't forget to drop user_sessions!
    op.drop_table('users')