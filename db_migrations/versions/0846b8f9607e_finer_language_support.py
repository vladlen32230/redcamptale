"""finer-language-support

Revision ID: 0846b8f9607e
Revises: 76ffdc2c67e2
Create Date: 2025-06-02 15:25:42.645763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0846b8f9607e'
down_revision: Union[str, None] = '76ffdc2c67e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to users table
    op.add_column('users', sa.Column('user_biography_displayed_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('user_biography_displayed_description', sa.String(), nullable=True))
    op.add_column('users', sa.Column('user_narrative_preference', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('user_narrative_displayed_preference', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('language', sa.String(), nullable=False, server_default='auto'))
    
    # Update the new columns with data from existing columns where possible
    # Set displayed name/description to the same as the original ones initially
    op.execute("UPDATE users SET user_biography_displayed_name = user_biography_name")
    op.execute("UPDATE users SET user_biography_displayed_description = user_biography_description")
    
    # Make the new columns non-nullable after setting default values
    op.alter_column('users', 'user_biography_displayed_name', nullable=False)
    op.alter_column('users', 'user_biography_displayed_description', nullable=False)
    
    # Drop old Russian-specific columns from users table
    op.drop_column('users', 'user_biography_russian_name')
    op.drop_column('users', 'user_biography_russian_description')
    
    # Add new column to messages table
    op.add_column('messages', sa.Column('displayed_text', sa.String(), nullable=True))
    
    # Migrate data from russian_translation to displayed_text (use english_text if russian_translation is null)
    op.execute("UPDATE messages SET displayed_text = COALESCE(russian_translation, english_text)")
    
    # Make displayed_text non-nullable after migration
    op.alter_column('messages', 'displayed_text', nullable=False)
    
    # Drop old russian_translation column from messages table
    op.drop_column('messages', 'russian_translation')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back old columns to messages table
    op.add_column('messages', sa.Column('russian_translation', sa.String(), nullable=True))
    
    # Migrate data back from displayed_text to russian_translation
    op.execute("UPDATE messages SET russian_translation = displayed_text WHERE russian_translation IS NULL")
    
    # Drop new column from messages table
    op.drop_column('messages', 'displayed_text')
    
    # Add back old Russian-specific columns to users table
    op.add_column('users', sa.Column('user_biography_russian_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('user_biography_russian_description', sa.String(), nullable=True))
    
    # Drop new columns from users table
    op.drop_column('users', 'language')
    op.drop_column('users', 'user_narrative_displayed_preference')
    op.drop_column('users', 'user_narrative_preference')
    op.drop_column('users', 'user_biography_displayed_description')
    op.drop_column('users', 'user_biography_displayed_name')
