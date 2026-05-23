from abc import ABC, abstractmethod

# --- 1. THE ABSTRACT CLASS ---
class Character(ABC):
    def __init__(self, name, health):
        self.name = name
        self.health = health

    @abstractmethod
    def attack(self):
        pass

    @abstractmethod
    def special_skill(self):
        pass

# --- 2. THE SUBCLASSES ---
class GlitchEntity(Character):
    def __init__(self, name, health=120):
        # Using the older super() format for maximum compatibility
        super(GlitchEntity, self).__init__(name, health)

    def attack(self):
        return "[" + self.name + "] slashes with corrupted static claws!"

    def special_skill(self):
        return "[" + self.name + "] uses Phase Shift to dodge!"

class Warrior(Character):
    def __init__(self, name, health=250):
        super(Warrior, self).__init__(name, health)

    def attack(self):
        return "[" + self.name + "] swings a massive steel broadsword!"

    def special_skill(self):
        return "[" + self.name + "] uses Shield Wall to block damage."

# --- 3. EXECUTION AND OUTPUT ---
my_glitch = GlitchEntity("Null_Pointer")
my_warrior = Warrior("Leonidas")

print("--- " + my_glitch.name + " ---")
print("Class: GlitchEntity")
print("Health: " + str(my_glitch.health))
print("Attack: " + my_glitch.attack())
print("Skill: " + my_glitch.special_skill())

print("\n------------------------------\n")

print("--- " + my_warrior.name + " ---")
print("Class: Warrior")
print("Health: " + str(my_warrior.health))
print("Attack: " + my_warrior.attack())
print("Skill: " + my_warrior.special_skill())
