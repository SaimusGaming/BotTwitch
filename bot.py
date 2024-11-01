import json
import asyncio
from twitchio.ext import commands

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

    @commands.command(name="pasedebatalla")
    async def pase_de_batalla(self, ctx):
        usuario = ctx.author.name.lower()
        if usuario not in self.user_data["inscritos_pase_de_batalla"]:
            self.user_data["inscritos_pase_de_batalla"][usuario] = True
            self.user_data["user_experience"][usuario] = {"nivel": 1, "experiencia_acumulada": 0, "experiencia_restante": 10000}
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
        # Si no se proporciona un usuario, usa el autor del mensaje
        if user is None:
            user = ctx.author.name.lower()

        # Obtener información de experiencia del usuario
        if user in self.user_data["user_experience"]:
            experiencia = self.user_data["user_experience"][user]["experiencia_acumulada"]
            nivel = self.get_user_level(experiencia)
            await ctx.send(f"{user}, tu nivel actual es {nivel}. Sigue ganando puntos viendo el streaming!")
        else:
            await ctx.send(f"{user}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")

    def get_user_level(self, experiencia):
        # Determina el nivel del usuario basado en su experiencia total
        if experiencia < 10000:
            return 1
        elif experiencia < 20000:
            return 2
        elif experiencia < 30000:
            return 3
        elif experiencia < 40000:
            return 4
        elif experiencia < 50000:
            return 5
        elif experiencia < 60000:
            return 6
        elif experiencia < 70000:
            return 7
        elif experiencia < 80000:
            return 8
        elif experiencia < 90000:
            return 9
        elif experiencia < 100000:
            return 10
        elif experiencia < 110000:
            return 11
        elif experiencia < 120000:
            return 12
        elif experiencia < 130000:
            return 13
        elif experiencia < 140000:
            return 14
        elif experiencia < 150000:
            return 15
        elif experiencia < 160000:
            return 16
        elif experiencia < 170000:
            return 17
        elif experiencia < 180000:
            return 18
        elif experiencia < 190000:
            return 19
        elif experiencia < 200000:
            return 20
        elif experiencia < 210000:
            return 21
        elif experiencia < 220000:
            return 22
        elif experiencia < 230000:
            return 23
        elif experiencia < 240000:
            return 24
        elif experiencia < 250000:
            return 25
        elif experiencia < 260000:
            return 26
        elif experiencia < 270000:
            return 27
        elif experiencia < 280000:
            return 28
        elif experiencia < 290000:
            return 29
        elif experiencia < 300000:
            return 30
        else:
            return "MAESTRO"  # Nivel maestro después del 30

    @commands.command(name="canje")
    async def canje(self, ctx, reward_level: int = None):
        usuario = ctx.author.name.lower()
    
        # Verificar si el usuario está inscrito y tiene datos de experiencia
        if usuario not in self.user_data["user_experience"]:
            await ctx.send(f"{usuario}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")
            return
    
        # Si no se proporciona un nivel, enviar un mensaje de ayuda
        if reward_level is None:
            await ctx.send(f"{usuario}, por favor especifica el nivel de recompensa que deseas canjear. Ejemplo: `!canje 1`")
            return
    
        # Obtener datos del usuario
        data = self.user_data["user_experience"][usuario]
        nivel_actual = data["nivel"]
    
        # Comprobar si la recompensa existe
        if reward_level in self.rewards:
            required_level = self.rewards[reward_level]["nivel_requerido"]
            if nivel_actual >= required_level:
                # Desbloquear la recompensa
                await ctx.send(f"{usuario} ha desbloqueado {self.rewards[reward_level]['name']} por alcanzar el nivel {nivel_actual}.")
            else:
                # No ha alcanzado el nivel requerido
                next_reward_level = min(filter(lambda x: x > nivel_actual, self.rewards.keys()), default=None)
                if next_reward_level:
                    next_required_level = self.rewards[next_reward_level]["nivel_requerido"]
                    await ctx.send(f"{usuario}, no has alcanzado el nivel requerido para canjear esta recompensa. Tu nivel actual es {nivel_actual} y necesitas alcanzar el nivel {next_required_level} para la próxima recompensa.")
                else:
                    await ctx.send(f"{usuario}, no hay más recompensas disponibles para tu nivel actual.")
        else:
            await ctx.send(f"{usuario}, la recompensa que intentas canjear no existe.")
            
    @commands.command(name="canje")
    async def canje(self, ctx, reward_level: int = None):
        usuario = ctx.author.name.lower()
    
        # Verificar si el usuario está registrado en el sistema
        if usuario not in self.user_data["user_experience"]:
            await ctx.send(f"{usuario}, no estás inscrito en el Pase de Batalla. Usa !pasedebatalla para inscribirte.")
            return
    
        # Si no se proporciona un nivel, enviar un mensaje de ayuda
        if reward_level is None:
            await ctx.send(f"{usuario}, por favor especifica el nivel de recompensa que deseas canjear. Ejemplo: `!canje 1`")
            return
    
        # Obtener datos del usuario
        data = self.user_data["user_experience"][usuario]
        nivel_actual = data["nivel"]
    
        # Inicializar la lista de recompensas canjeadas si no existe en los datos del usuario
        if "recompensas_canjeadas" not in data:
            data["recompensas_canjeadas"] = []
    
        # Verificar si la recompensa ya fue canjeada
        if reward_level in data["recompensas_canjeadas"]:
            # Encontrar el próximo nivel con recompensa disponible
            next_reward_level = min(
                (level for level in self.rewards if level > nivel_actual and level not in data["recompensas_canjeadas"]),
                default=None
            )
            if next_reward_level:
                next_required_level = self.rewards[next_reward_level]["nivel_requerido"]
                await ctx.send(f"{usuario}, ya has canjeado esta recompensa. La siguiente recompensa está disponible en el nivel {next_required_level}.")
            else:
                await ctx.send(f"{usuario}, ya has canjeado todas las recompensas disponibles para tu nivel actual.")
            return
    
        # Comprobar si la recompensa existe y si el nivel del usuario es suficiente
        if reward_level in self.rewards:
            required_level = self.rewards[reward_level]["nivel_requerido"]
            if nivel_actual >= required_level:
                # Desbloquear la recompensa y añadirla a la lista de recompensas canjeadas
                data["recompensas_canjeadas"].append(reward_level)
                await ctx.send(f"{usuario} ha desbloqueado {self.rewards[reward_level]['name']} por alcanzar el nivel {nivel_actual}.")
                # Guardar los datos
                self.save_data()
            else:
                # Si el nivel no es suficiente, buscar el próximo nivel con recompensa
                next_reward_level = min(
                    (level for level in self.rewards if level > nivel_actual),
                    default=None
                )
                if next_reward_level:
                    next_required_level = self.rewards[next_reward_level]["nivel_requerido"]
                    await ctx.send(f"{usuario}, no has alcanzado el nivel requerido para canjear esta recompensa. Tu nivel actual es {nivel_actual} y necesitas alcanzar el nivel {next_required_level} para la próxima recompensa.")
                else:
                    await ctx.send(f"{usuario}, no hay más recompensas disponibles para tu nivel actual.")
        else:
            await ctx.send(f"{usuario}, la recompensa que intentas canjear no existe.")
    
    @commands.command(name="info")
    async def info(self, ctx):
        await ctx.send("¡Hazte con tu Pase de Batalla Temporada 1 de SaimusGaming! *Puntos por seguidor: 85/minuto, *Puntos suscriptor: 95/minuto. ¡Consigue recompensas apoyando el canal! Más información sobre recompensas y el Pase completo en http://SaimusGaming.es")
bot = Bot()
bot.run()
