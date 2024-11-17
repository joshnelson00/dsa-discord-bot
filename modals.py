import discord
from question_serve import get_options, get_problem
class dsa(discord.ui.Select):
    def __init__(self):

        options = get_options()

        super().__init__(placeholder='Select a topic to practice', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        get_problem(self.values[0])
        await interaction.response.send_message(f'You selected {self.values[0]}')

class dsa_dropdown_view(discord.ui.View):
    def __init__(self):
        super().__init__()
        # Adds the dropdown to our view object.
        self.add_item(dsa())

