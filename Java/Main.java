class Demo {
    int num;

    Demo(int num) {
        this.num = num;
    }

    int getNum() {
        return num;
    }
}

class Main {
    public static void main(String[] args) {
        Demo obj1 = new Demo(10);
        System.out.println(obj1.getNum());
    }
}
