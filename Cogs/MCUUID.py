import json
import requests
import discord
from pytz import timezone
from discord.ext import commands


class MCUUID(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)

    def load_json(self):
        load_file = open('ban_list.json', 'r', encoding="utf-8_sig")
        json_data = json.load(load_file)
        load_file.close
        return json_data

    def save_json(self, json_data):
        save_file = open('ban_list.json', 'w')
        json.dump(json_data, save_file)
        save_file.close

    def get_uuid(self, mcid: str):
        url = 'https://api.mojang.com/users/profiles/minecraft/{0}'.format(
            mcid)
        res = requests.get(url)

        status_code = res.status_code
        return res, status_code

    @commands.command(name='uuid')
    async def _uuid(self, ctx: commands.context, mcid: str):
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            uuid = res.json()['id']
            await ctx.send(uuid)
        else:
            await ctx.send('サーバーエラー')

    @commands.command(name='ban')
    async def _ban(self, ctx: commands.context, mcid: str, reson: str):
        json_data = self.load_json()
        if mcid in json_data:
            await ctx.send('このIDはすでにBAN登録されています')
            return

        registerer = ctx.author.nick
        message_link = 'https://discord.com/channels/{0}/{1}/{2}'.format(
            ctx.guild.id, ctx.message.channel.id, ctx.message.id)
        created_at_utc = ctx.message.created_at
        created_at_jst = created_at_utc.astimezone(
            timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
        res, status_code = self.get_uuid(mcid)
        if status_code == 204:
            await ctx.send('IDが見つかりませんでした')
            return
        elif status_code == 200:
            uuid = res.json()['id']
        else:
            await ctx.send('サーバーエラー')

        json_data[mcid] = {
            "uuid": uuid,
            "reason": reson,
            "registerer": registerer,
            "time": created_at_jst,
            "message_link": message_link
        }

        self.save_json(json_data)

        await ctx.send('登録しました')

    @commands.command(name='search')
    async def _search(self, ctx, mcid):
        json_data = self.load_json()
        if mcid not in json_data:
            await ctx.send('見つかりませんでした。')
            return

        user_data = json_data[mcid]
        uuid = user_data['uuid']
        reason = user_data['reason']
        registerer = user_data['registerer']
        time = user_data['time']
        message_link = user_data['message_link']
        face_url = f'https://crafatar.com/avatars/{uuid}'

        embed = discord.Embed(
            title=mcid, description=uuid, color=0xff0000)
        embed.set_thumbnail(
            url=face_url)
        embed.add_field(name="BAN理由", value=reason, inline=False)
        embed.add_field(name="BAN登録", value=registerer, inline=True)
        embed.add_field(name="日時", value=time, inline=True)
        embed.add_field(
            name="リンク", value=f"[{message_link}]({message_link})", inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(MCUUID(bot))
