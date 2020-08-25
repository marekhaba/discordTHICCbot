import secrets
import discord
from PIL import Image
from requests import get as req_get
from io import BytesIO
import math
from discord.ext import commands
import asyncio
import concurrent

client = commands.Bot("!")
client.remove_command("help")

def bulge_compute(input_img, rel_x, rel_y, bulge_strength, rel_Radius, output_img):
    input_ = input_img.load()
    output_ = output_img.load()
    w = input_img.size[0]
    h = input_img.size[1]
    cx = w*rel_x
    cy = h*rel_y
    bulge_Radius = ((w+h)//2)*(rel_Radius)
    for x in range(0,w):
        for y in range(0,h):
            dx = x-cx
            dy = y-cy
            distanceSquared = dx * dx + dy * dy
            sx = x
            sy = y
            if distanceSquared < (bulge_Radius * bulge_Radius):
                distance = math.sqrt(distanceSquared)
                r = distance / bulge_Radius
                a = math.atan2(dy, dx)
                rn = math.pow(r, bulge_strength)*distance
                newx = rn*math.cos(a) + cx
                newy = rn*math.sin(a) + cy
                sx += (newx - x)
                sy += (newy - y)
            if (sx >= 0 and sx < w and sy >= 0 and sy < h):
                rgb = input_[sx, sy]
                output_[x, y] = rgb

@client.event
async def on_ready():
    print(f'logged in as {client.user}')

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)} ms")

@client.command()
async def thicc(ctx, *args):
    """
    args either nothing or :\n
    "x=0.5 y=0.5 strength=0.5 radius=0.5"\n
    """
    embed = discord.Embed(
        title=":gear: Working...",
        description="This may take a while depending on your image size.",
        colour = discord.Colour.green()
    )
    #embed.set_footer(text="I just copied some random bulge algroithm from the net and done 0 optimization s thats probably thy this is so slow.")
    working_message = await ctx.send(embed=embed)
    x = 0.5
    y = 0.5
    strength = 0.5
    radius = 0.5
    for arg in args:
        params = arg.split("=")
        if params[0] == "x":
            x=float(params[1])
        elif params[0] == "y":
            y=float(params[1])
        elif params[0] == "strength":
            strength=float(params[1])
        elif params[0] == "radius":
            radius=float(params[1])

    response = req_get(ctx.message.attachments[0].url)
    img = Image.open(BytesIO(response.content))

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    loop = asyncio.get_event_loop()
    out = await loop.run_in_executor(executor, img.copy)

    await loop.run_in_executor(executor, bulge_compute, img, x, y, strength, radius, out)

    output = BytesIO()
    out.save(output, format="png")
    output.seek(0)
    file = discord.File(output, "thicc.png")
    await working_message.delete()
    await ctx.message.delete()
    await ctx.send(file=file)

@client.command(pass_context=True)
async def help(ctx):

    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name="help")
    embed.add_field(name="!thicc", value="write with an image to make it THICC\n x=0...1 --x relative to the image size \n y=0...1  --y relative to the image size \n strength=0...1 --strength of the bulge \n radius=0...1 --radius of the bulge relative to the image size")

    await ctx.send(embed=embed)

client.run(secrets.token)