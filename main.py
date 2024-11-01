import json
import asyncio
from twitchio.ext import commands
import aiohttp

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token='bkx0tdk3sks2q0yvkdp920apayilzr', prefix='!', initial_channels=['SaimusGaming'])
        self.user_data_file = "data.json"
        self.load_data()
        self.experience_per_minute = {"seguidor": 85, "suscriptor": 95}
        self.level_requirements = [10000 * i for i in range(1, 31)]

        # Definir recompensas
        self.rewards = {
            1: {"name": "Skin básica", "nivel_requerido": 1},
            2: {"name": "Cofre sorpresa", "nivel_requerido": 2},
            3: {"name": "Participación en sorteo", "nivel_requerido": 3},
            4: {"name": "Skin premium", "nivel_requerido": 5},
            5: {"name": "Club de Fortnite", "nivel_requerido": 10},
        }

    def load_data(self):
        try:
            with open(self.user_data_file, "r") as f:
                self.user_data = json.load(f)
        except FileNotFoundError:
            self.user_data = {"user_experience": {}, "inscritos_pase_de_batalla": {}}

    def save_data(self):
        with open(self.user_data_file, "w") as f:
            json.dump(self.user_data, f, indent=4)

    async def event_ready(self):
        print(f"Bot conectado como {self.nick}")
        self.update_experience_task = self.loop.create_task(self.update_experience_periodically())

    async def update_experience_periodically(self):
        while True:
            if await self.is_channel_online():
                for user, data in self.user_data["user_experience"].items():
                    if user in self.user_data["inscritos_pase_de_batalla"]:
                        role = "suscriptor" if data.get("es_suscriptor", False) else "seguidor"
                        data["experiencia_acumulada"] += self.experience_per_minute[role]

                        # Calcula el nivel según experiencia acumulada
                        for level, exp_required in enumerate(self.level_requirements, 1):
                            if data["experiencia_acumulada"] < exp_required:
                                data["nivel"] = level
                                data["experiencia_restante"] = exp_required - data["experiencia_acumulada"]
                                break
                        else:
                            data["nivel"] = "Maestro"
                            data["experiencia_restante"] = 0
                self.save_data()
            await asyncio.sleep(60)  # Espera un minuto antes de la siguiente actualización

    async def is_channel_online(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api.twitch.tv/helix/streams?user_login=SaimusGaming', headers={
                'Client-ID': 'tu_client_id_aqui',  # Reemplaza con tu Client ID
                'Authorization': 'Bearer tu_token_de_acceso_aqui'  # Reemplaza con tu token de acceso
            }) as response:
                data = await response.json()
                return data['data'] != []

    @commands.command(name="pasedebatalla")
    async def pase_de_batalla(self, ctx):
        usuario = ctx.author.name.lower()
        if usuario not in self.user_data["inscritos_pase_de_batalla"]:
            self.user_data["inscritos_pase_de_batalla"][usuario] = True
            self.user_data["user_experience"][usuario] = {"nivel": 1, "experiencia_acumulada": 0, "experiencia_restante": 10000, "recompensas_canjeadas": []}
            self.save_data()
            await ctx.send(f"{usuario} se ha inscrito al Pase de Batalla y ahora es Nivel 1.")
        else:
            await ctx.send(f"{usuario}, ya estás inscrito en el Pase de Batalla.")

    @commands.command(name="exp")
    async def exp(self, ctx):
        usuario = ctx.author.name.lower()
        if usuario in self.user_data["user_experience"]:
            data = self.user_data["user_experience"][usuario]
            if data["nivel"] == "Maestro":
                await ctx.send(f"{usuario}, eres Nivel Maestro con {data['experiencia_acumulada']} puntos de experiencia.")
            else:
                await ctx.send(f"{usuario}, tienes {data['experiencia_acumulada']} puntos de experiencia, necesitas {data['experiencia_restante']} puntos para alcanzar el Nivel {data['nivel'] + 1}.")
        else:
            await ctx.send(f"{usuario}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")

    @commands.command(name="level")
    async def level(self, ctx, user: str = None):
        if user is None:
            user = ctx.author.name.lower()

        if user in self.user_data["user_experience"]:
            experiencia = self.user_data["user_experience"][user]["experiencia_acumulada"]
            nivel = self.get_user_level(experiencia)
            await ctx.send(f"{user}, tu nivel actual es {nivel}. Sigue ganando puntos viendo el streaming!")
        else:
            await ctx.send(f"{user}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")

    def get_user_level(self, experiencia):
        for i, exp in enumerate(self.level_requirements):
            if experiencia < exp:
                return i + 1
        return "Maestro"

    @commands.command(name="canje")
    async def canje(self, ctx, reward_level: int = None):
        usuario = ctx.author.name.lower()

        if usuario not in self.user_data["user_experience"]:
            await ctx.send(f"{usuario}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")
            return

        if reward_level is None:
            await ctx.send(f"{usuario}, por favor especifica el nivel de recompensa que deseas canjear. Ejemplo: `!canje 1`")
            return

        data = self.user_data["user_experience"][usuario]
        nivel_actual = data["nivel"]

        if reward_level in data["recompensas_canjeadas"]:
            await ctx.send(f"{usuario}, ya has canjeado esta recompensa.")
            return

        if reward_level in self.rewards:
            required_level = self.rewards[reward_level]["nivel_requerido"]
            if nivel_actual >= required_level:
                data["recompensas_canjeadas"].append(reward_level)
                await ctx.send(f"{usuario} ha desbloqueado {self.rewards[reward_level]['name']} por alcanzar el nivel {nivel_actual}.")
                self.save_data()
            else:
                next_reward_level = min(
                    (level for level in self.rewards if level > nivel_actual),
                    default=None
                )
                if next_reward_level:
                    next_required_level = self.rewards[next_reward_level]["nivel_requerido"]
                    await ctx.send(f"{usuario}, no has alcanzado el nivel requerido para canjear esta recompensa. Tu nivel actual es {nivel_actual} y necesitas alcanzar el nivel {next_required_level}.")
                else:
                    await ctx.send(f"{usuario}, no hay recompensas disponibles.")
        else:
            await ctx.send(f"{usuario}, recompensa no válida. Por favor, selecciona un nivel de recompensa entre 1 y {len(self.rewards)}.")

    @commands.command(name="info")
    async def info(self, ctx):
        await ctx.send("¡Hazte con tu Pase de Batalla Temporada 1 de SaimusGaming! *Puntos por seguidor: 85/minuto, *Puntos suscriptor: 95/minuto. ¡Consigue recompensas apoyando el canal! Más información sobre recompensas y el Pase completo en http://SaimusGaming.es")

if __name__ == "__main__":
    bot = Bot()
    bot.run()
