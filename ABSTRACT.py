from abc import ABC, abstractmethod

# --- PART 1: THE ABSTRACT CLASS ---
class Character(ABC):
    def __init__(self, name, health):
        self.name = name
        self.health = health

    @abstractmethod
    def attack(self):
        """Must be overridden by subclasses to define how the character attacks."""
        pass

    @abstractmethod
    def special_skill(self):
        """Must be overridden by subclasses to define the character's unique ability."""
        pass


# --- PART 2: THE SUBCLASSES ---

class Survivor(Character):
    def __init__(self, name="The Scholar", health=100):
        # Initialize the parent class with name and health
        super().__init__(name, health)
        self.stamina = 100 

    def attack(self):
        return f"{self.name} swings a heavy, dusty library book! (It deals minimal damage...)"

    def special_skill(self):
        self.stamina -= 20
        return f"{self.name} uses 'Desperate Sprint'! They pull their grey trench coat tight and run at max speed to escape."


class ShadowEntity(Character):
    def __init__(self, name="The Pure Black Shadow", health=500):
        super().__init__(name, health)
        self.blast_cooldown = 0

    def attack(self):
        return f"{self.name}'s glowing white eyes narrow as it fires a brilliant, glowing blue blast!"

    def special_skill(self):
        return f"{self.name} uses 'Shadow Form'! Its pitch-black body absorbs the darkness, making it impossible to hide from."


# --- TEST THE CODE ---
if __name__ == "__main__":
    # Create instances of our subclasses
    player = Survivor()
    monster = ShadowEntity()

    print("--- GAME START ---")
    print(f"Player: {player.name} (HP: {player.health})")
    print(f"Enemy: {monster.name} (HP: {monster.health})\n")

    # Test Player Actions
    print("PLAYER TURN:")
    print(player.attack())
    print(player.special_skill())
    
    print("\n" + "-"*20 + "\n")

    # Test Entity Actions
    print("ENEMY TURN:")
    print(monster.special_skill())
    print(monster.attack())
