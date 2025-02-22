import discord
from discord.ext import commands, tasks
import os
from database.mainDatabase_db import Database, BirthdayTable
from sqlalchemy import select, insert, update, delete
from datetime import date, datetime, timedelta, time

class Stuff(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot: discord.Bot = bot
        self.db = Database()
        self.bot.loop.create_task(self.db.init_db())
        self.check_birthdays.start()
        self.remove_birthday_role.start()

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        now = datetime.now()
        target_time = time(14, 5)
        target_datetime = datetime.combine(now.date(), target_time)

        if now > target_datetime:
            target_datetime += timedelta(days=1)

        await discord.utils.sleep_until(target_datetime)

        today = target_datetime.date()
        users_with_birthday = await self.db.get_users_with_birthday(today.day, today.month)
        for user in users_with_birthday:
            guild: discord.Guild = self.bot.get_guild(user.guild_id)
            member = guild.get_member(user.user_id)
            if member:
                amaunzment = guild.get_channel_or_thread(1191397658514956308)
                birthdayRole = guild.get_role(1342827586648150076)
                try:
                    if user.year == 1900:
                        await amaunzment.send(f"Happy Birthday, <@{member.id}>! :birthday: ")
                        await member.add_roles(birthdayRole)
                    else:
                        await amaunzment.send(f"Happy Birthday, <@{member.id}>! :birthday:\nYou're now {today.year - user.year} years old!")
                        await member.add_roles(birthdayRole)
                except Exception as e:
                    print(e)
    
    @tasks.loop(hours=24)
    async def remove_birthday_role(self):
        now = datetime.now()
        target_time = time(14, 8)
        target_datetime = datetime.combine(now.date(), target_time)

        if now > target_datetime:
            target_datetime += timedelta(days=1)

        await discord.utils.sleep_until(target_datetime)
        bdRoleMembers = self.bot.get_guild(1056514064081231872).get_role(1342827586648150076).members
        for member in bdRoleMembers:
            await member.remove_roles(self.bot.get_guild(1056514064081231872).get_role(1342827586648150076))

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()
                    
    @discord.slash_command(name="ping", description="Pong!", contexts={discord.InteractionContextType.guild})
    async def pull(self, ctx):
        await ctx.respond("Pong!")

    birthdayCommandGroup = discord.SlashCommandGroup(name="birthday", description="A selection of birthday commands.", contexts={discord.InteractionContextType.guild})
    @birthdayCommandGroup.command(name="set", description="Set your birthday.", contexts={discord.InteractionContextType.guild})
    @discord.option(name="day", description="The day of your birthday.", type=discord.SlashCommandOptionType.integer, required=True)
    @discord.option(name="month", description="The month of your birthday.", type=discord.SlashCommandOptionType.integer, required=True)
    @discord.option(name="year", description="The year of your birthday.", type=discord.SlashCommandOptionType.integer, required=False)
    async def setBirthday(self, ctx, day: int, month: int, year: int = 1900):
        birthday = None
        try:
            birthday = date(year, month, day)
        except ValueError:
            return await ctx.respond("Invalid date.", ephemeral=True)
        
        if birthday > date.today():
            return await ctx.respond("You can't set a birthday in the future.", ephemeral=True)
        try:
            if await self.db.get_user_record(ctx.author.id, ctx.guild.id) is None:
                await self.db.create_user_record(ctx.author.id, ctx.guild.id, birthday)
                await ctx.respond("Birthday set!")
            else:
                await self.db.edit_user_record(ctx.author.id, ctx.guild.id, birthday)
                await ctx.respond("Birthday updated!")
        except Exception as e:
            await ctx.respond("An error occurred. Please try again later.", ephemeral=True)
            print(e)
    @birthdayCommandGroup.command(name="delete", description="Delete your birthday.", contexts={discord.InteractionContextType.guild})
    async def deleteBirthday(self, ctx):
        try:
            await self.db.delete_user_record(ctx.author.id, ctx.guild.id)
            await ctx.respond("Birthday deleted!")
        except Exception as e:
            await ctx.respond("An error occurred. Please try again later.", ephemeral=True)
            print(e)

    

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Stuff(bot)) # add the cog to the bot