public class Main {
    public static void main(String[] args) {
        String str1 = new String("Hello");
        String str2 = new String("Hello");
        String str3 = str1;

        // Using equals() method
        System.out.println("Using equals() method:");
        System.out.println("str1.equals(str2): " + str1.equals(str2)); // true
        System.out.println("str1.equals(str3): " + str1.equals(str3)); // true

        // Using == operator
        System.out.println("\nUsing == operator:");
        System.out.println("str1 == str2: " + (str1 == str2)); // false
        System.out.println("str1 == str3: " + (str1 == str3)); // true

        // Integer comparison
        Integer num1 = 5;
        Integer num2 = 5;
        Integer num3 = new Integer(5);

        System.out.println("\nInteger comparison:");
        System.out.println("num1 == num2: " + (num1 == num2)); // true
        System.out.println("num1 == num3: " + (num1 == num3)); // false

        // Object comparison
        Object obj1 = new Object();
        Object obj2 = new Object();
        Object obj3 = obj1;

        System.out.println("\nObject comparison:");
        System.out.println("obj1 == obj2: " + (obj1 == obj2)); // false
        System.out.println("obj1 == obj3: " + (obj1 == obj3)); // true
    }
}
