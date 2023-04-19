class Animal {
    String name;

    Animal(String name) {
        this.name = name;
    }

    void eat() {
        System.out.println("Animal is eating");
    }
}

class Dog extends Animal {
    int age;

    Dog(String name, int age) {
        super(name);
        this.age = age;
    }

    void eat() {
        super.eat(); // calls the Animal's eat() method
        System.out.println("Dog is eating");
    }
}

public class Main {
    public static void main(String[] args) {
        Dog dog = new Dog("Tommy", 5);
        dog.eat();
    }
}
