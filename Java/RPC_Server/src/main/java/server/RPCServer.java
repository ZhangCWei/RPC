package server;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.lang.reflect.Method;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;

import controller.TestService;
import repository.Test;


public class RPCServer {
    private int port;
    private Map<String, Object> serviceMap = new HashMap<>();
    public RPCServer(int port) {
        this.port = port;
    }
    public void register(String serviceName, Object service) {
        serviceMap.put(serviceName, service);
    }
    public void start() throws IOException, InterruptedException, ExecutionException {
    	ServerSocket serverSocket = new ServerSocket(port);
    	//serverSocket.bind(new InetSocketAddress("192.168.43.50", port));
        while (true) {	
        	final Socket socket = serverSocket.accept();
        	socket.setSoTimeout(2000);
        	InetAddress ip = socket.getInetAddress();   
            ExecutorService executor = Executors.newFixedThreadPool(200);    
            FutureTask<String> future =    
                   new FutureTask<String>(new Callable<String>() {   
                     public String call() {    
                    	 try {
                             InputStream in = socket.getInputStream();
                             OutputStream out = socket.getOutputStream();
                             byte[] buffer = new byte[1024];
                             int len = in.read(buffer);
                             String requestJson = new String(buffer, 0, len);
                             JSONObject request = JSON.parseObject(requestJson);
                             String serviceName = request.getString("FuncName");
                             String methodName = request.getString("methodName");

                             Object service = null;         
                             Object result = null;
                             if (serviceName.equals("list")) 
                            {
                            		 service = serviceMap.get("default");
                                	 result = GetServices(service.getClass());                             	 
                            }
                            else if(methodName == null)
                             {
                                 Object[] args = request.getJSONArray("Args").toArray();
                        		 service = serviceMap.get("default"); 
                        		 Method method = service.getClass().getMethod(serviceName, getParameterTypes(args));
                                 if(method == null){
                                	 throw new RuntimeException("service not found: " + serviceName);
                                 }   
                                 result = method.invoke(service, args);
                             }
                             else { 
                                Object[] args = request.getJSONArray("Args").toArray();
                                service = serviceMap.get(serviceName);
                                Method method = service.getClass().getMethod(methodName, getParameterTypes(args));
                                if(method == null){
                                throw new RuntimeException("service not found: " + serviceName);
                                }   
                                result = method.invoke(service, args);	                          	
                                	
							}
                        
                             Map<String, Object> response = new HashMap<>();
                             response.put("result", result.toString());
                             String responseJson = JSON.toJSONString(response);
                             out.write(responseJson.getBytes());
                             out.flush();
                             
                         } catch (Exception e) {
                             e.printStackTrace();
                             Map<String, Object> response = new HashMap<>();
                             response.put("exception", e.getMessage());
                             String responseJson = JSON.toJSONString(response);
                             try {
                                 socket.getOutputStream().write(responseJson.getBytes());
                                 socket.getOutputStream().flush();
                             } catch (IOException ex) {
                                 ex.printStackTrace();
                             }
                         } finally {
                             try {
                                 socket.close();
                             } catch (IOException e) {
                                 e.printStackTrace();
                             }
                         }
						return "well done";
						}});    
            executor.execute(future);      
            try {    
                System.out.println(future.get(5000, TimeUnit.MILLISECONDS)); 
            }catch (TimeoutException e) {    
                break;    
            } finally {    
                executor.shutdown();    
            }    
          
        }
    }

    private Class<?>[] getParameterTypes(Object[] args) {
        Class<?>[] parameterTypes = new Class<?>[args.length];
        for (int i = 0; i < args.length; i++) {
            parameterTypes[i] = args[i].getClass();
        }
        return parameterTypes;
    }
	private Object GetServices(Class service) {
    	Method[] methods = service.getDeclaredMethods();
    	Vector<Map<String, Object>> serviceList = new Vector<Map<String, Object>>();
    	for(int i=0;i<methods.length;i++)
    	{
    		if(i%2==0)
    		{
       		 Map<String, Object> method = new HashMap<String, Object>();
       		 method.put("service", methods[i].getName());
       		 method.put("return", methods[i].getReturnType());
       		 method.put("params", methods[i].getParameterTypes());
       		 serviceList.add(method);
    		}
    	}
    	return serviceList;
	}
    
    public static void main(String args[]) throws IOException, InterruptedException, ExecutionException 
    {   
    	RPCServer server = new RPCServer(8001);
    	Test test = new TestService();
    	server.register("default", test);
    	server.start();
	}
    

}

