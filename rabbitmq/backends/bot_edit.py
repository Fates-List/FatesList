import discord
from modules.core import add_event
from config import bot_logs
import asyncio

"""
    For later (if more scaling is required):

        Use this to make bot owners in db. Use similar for bot tags

            owners = await connection.fetch("SELECT owner FROM bot_owner where bot_id = $1 AND main = false", bot_id)
            extra_owners_ignore = [] # Extra Owners to ignore because they have already been counted in the database (already extra owners)
            extra_owners_delete = [] # Extra Owners to delete
            extra_owners_add = [] # Extra Owners to add
            for owner in owners: # Loop through owners and add to delete list if not in new extra owners
                if owner["owner"] not in extra_owners:
                    extra_owners_delete.append((bot_id, owner["owner"]))
                else:
                    extra_owners_ignore.append(owner["owner"]) # Ignore this user when adding users
            await connection.executemany("DELETE FROM bot_owner WHERE bot_id = $1 AND owner = $2 AND main = false", extra_owners_delete) # Delete in one step
            for owner in extra_owners:
                if owner not in extra_owners_ignore:
                    extra_owners_add.append((bot_id, owner, False)) # If not in ignore list, add to add list
            await connection.executemany("INSERT INTO bot_owner (bot_id, owner, main) VALUES ($1, $2, $3)", extra_owners_add) # Add in one step
"""


async def bot_edit_backend(user_id, bot_id, prefix, library, website, banner, support, long_description, description, tags, extra_owners, creation, invite, webhook, vanity, github, features, long_description_type, webhook_type, css, donate, privacy_policy, nsfw):
    await db.execute("UPDATE bots SET bot_library=$2, webhook=$3, description=$4, long_description=$5, prefix=$6, website=$7, discord=$8, banner=$9, invite=$10, github = $11, features = $12, long_description_type = $13, webhook_type = $14, css = $15, donate = $16, privacy_policy = $17, nsfw = $18 WHERE bot_id = $1", bot_id, library, webhook, description, long_description, prefix, website, support, banner, invite, github, features, long_description_type, webhook_type, css, donate, privacy_policy, nsfw) # Update bot with new info

    async with db.acquire() as connection: # Acquire a connection
        async with connection.transaction() as tr: # Make a transaction to avoid data loss
            await db.execute("DELETE FROM bot_owner WHERE bot_id = $1 AND main = false", bot_id) # Delete all extra owners
            for owner in extra_owners:
                await db.execute("INSERT INTO bot_owner (bot_id, owner, main) VALUES ($1, $2, $3)", bot_id, owner, False)


    async with db.acquire() as connection: # Acquire a connection
        async with connection.transaction() as tr: # Make a transaction to avoid data loss
            await db.execute("DELETE FROM bot_tags WHERE bot_id = $1", bot_id) # Delete all bot tags
            for tag in tags:
                await db.execute("INSERT INTO bot_tags (bot_id, tag) VALUES ($1, $2)", bot_id, tag) # Insert new bot tags


    async with db.acquire() as connection:
        async with connection.transaction():
            check = await connection.fetchrow("SELECT vanity FROM vanity WHERE redirect = $1", bot_id) # Check vanity existance
            if check is None:
                if vanity.replace(" ", "") != '': # If not there for this bot, insert new one
                    await connection.execute("INSERT INTO vanity (type, vanity_url, redirect) VALUES ($1, $2, $3)", 1, vanity, bot_id)
            else:
                if vanity == '':
                    vanity = None # If vanity is expty string, there is no vanity

                await connection.execute("UPDATE vanity SET vanity_url = $1 WHERE redirect = $2", vanity, bot_id) # Update the vanity since bot already use it
    await bot_add_event(bot_id, "edit_bot", {"user": str(user_id)}) # Send event
    channel = client.get_channel(bot_logs)
    owner = int(user_id)
    edit_embed = discord.Embed(title="Bot Edit!", description=f"<@{owner}> has edited the bot <@{bot_id}>!", color=0x00ff00)
    edit_embed.add_field(name="Link", value=f"https://fateslist.xyz/bot/{bot_id}")
    await channel.send(embed = edit_embed) # Send message to channel
