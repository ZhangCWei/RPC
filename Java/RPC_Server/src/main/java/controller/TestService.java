package controller;

import repository.Test;

public class TestService implements Test{

	public float add(String a, String b) {
		float A = Float.parseFloat(a);
		float B = Float.parseFloat(b);
		return add(A, B);
	}
	public float add(float a, float b) {
		return a+b;
	}
	
	public float sub(String a, String b) {
		float A = Float.parseFloat(a);
		float B = Float.parseFloat(b);
		return sub(A, B);
	}
	public float sub(float a, float b) {
		return a-b;
	}
	
	public float multi(String a, String b) {
		float A = Float.parseFloat(a);
		float B = Float.parseFloat(b);
		return multi(A, B);
	}
	public float multi(float a, float b) {
		return a*b;
	}
	
	public float minus(String a) {
		float A = Float.parseFloat(a);
		return minus(A);
	}
	public float minus(float a) {
		return -a;	
	}
	
	public float square(String a) {
		float A = Float.parseFloat(a);
		return square(A);
	}
	public float square(float a) {
		return a*a;
	}
	
	public float cube(String a) {
		float A = Float.parseFloat(a);
		return cube(A);
	}
	public float cube(float a) {
		return a*a*a;
	}
	
	public String joint(String a, String b) {
		return a.concat(b);
	}

	public String mprint(String a) {
		System.out.println(a);
		return a;
	}
	
	public boolean ParityJudge(String a) {
		Integer A = Integer.parseInt(a);
		return ParityJudge(A);
	}
	
	public boolean ParityJudge(Integer a) {
		if(a%2==0)
			return true;
		else {
			return false;
		}
	}
	
	public boolean PNJudge(String a) {
		float A = Float.parseFloat(a);
		return PNJudge(A);
	}
	public boolean PNJudge(float a) {
		if(a>0)
		  return true;
		else
		  return false;

	}
	
	
}
