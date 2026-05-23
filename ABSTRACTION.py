from abc import ABC, abstractmethod

# --- Part 1 - Abstract Class Character ---

class Character(ABC):
    """
    Abstract Base Class for all game characters.
    Defines common attributes and required methods.
    """
    
    def __init__(self, name: str, health: int):
        self.name = name
        self.health = health
        self.is_alive = True
        print(f"{self.name} has entered the game with {self.health} health.")

    @abstractmethod
    def attack(self):
        """Must be overridden by subclasses to describe an attack action."""
        pass

    @abstractmethod
    def special_skill(self):
        """Must be overridden by subclasses to describe a special skill."""
        pass

    def take_damage(self, damage_amount: int):
        """Reduces character health and updates alive status."""
        self.health -= damage_amount
        print(f"{self.name} took {damage_amount} damage. Current health: {self.health}")
        if self.health <= 0:
            self.is_alive = False
            print(f"{self.name} has been defeated!")


# --- Part 2 - Subclasses based on the provided images ---

class ShadowEntity(Character):
    """
    A mysterious, shadowy entity that glitches and performs energy attacks.
    Reference sprites: image_0.png, image_6.png
    """
    
    def attack(self):
        """Overrides Character.attack() based on energy beams in image_6.png."""
        action_desc = f"{self.name} unleashed a torrent of flickering white and purple energy beams, glitching reality as they surge forward!"
        print(action_desc)
        return action_desc

    def special_skill(self):
        """Overrides Character.special_skill() based on glitch dash in image_0.png."""
        action_desc = f"{self.name} activated 'Glitched Phasedash', rapidly teleporting forward while distorted motion blurs and reality trails follow!"
        print(action_desc)
        return action_desc


class Survivor(Character):
    """
    A human survivor navigating a harsh world.
    Reference sprites: image_3.png, image_4.png
    """
    
    def attack(self):
        """Overrides Character.attack() with improvised melee suitable for the adventurer."""
        # Note: Descriptions derived from image reference only for citations.
        action_desc = f"{self.name} swings a sturdy, scavenged wrench with desperate force, aiming to strike the closest foe."
        print(action_desc)
        return action_desc

    def special_skill(self):
        """Overrides Character.special_skill() with a survival crafting skill."""
        # Note: Descriptions derived from image reference only for citations.
        action_desc = f"{self.name} quickly gathered materials to craft a makeshift bandage, restoring a small amount of health!"
        print(action_desc)
        return action_desc


# --- Example Usage ---

if __name__ == "__main__":
    print("\n--- Game Initialization ---\n")
    
    # Create instances of the characters
    player_survivor = Survivor(name="Human Adventurer", health=100)
    shadow_enemy = ShadowEntity(name="Mysterious Entity", health=250)
    
    print("\n--- Gameplay Loop Simulation ---\n")
    
    # Simulate a few turns/actions
    player_survivor.attack()
    print("-" * 20)
    shadow_enemy.special_skill()
    print("-" * 20)
    shadow_enemy.attack()
    print("-" * 20)
    
    # Shadow Entity deals damage
    player_survivor.take_damage(25)
    print("-" * 20)
    
    player_survivor.special_skill()
    print("-" * 20)
    
    shadow_enemy.attack()
    print("-" * 20)
    
    player_survivor.take_damage(80) # Defeats the player
