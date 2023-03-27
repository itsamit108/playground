class Demo {
    void join(int a, int b){
        System.out.println(a+b);
    }
    void join(double a, double b){
        System.out.println(a+b);
    }
    void join(String a, String b){
        System.out.println(a+b);
    }
}

class Main {
    public static void main(String[] args) {
        Demo obj1=new Demo();
        obj1.join(1,2);
        obj1.join(1.5,2.5);
        obj1.join("Hello ", "World");
    }
}
