# zomato_data_analysis
Zomato Order Data Analysis

1.) Install FastAPI<br>
  ```
     pip3 install fastapi 
     pip3 install "uvicorn[standard]" 
  ```
  FastAPI [Doc Link](https://fastapi.tiangolo.com/tutorial/first-steps/)
<br>
2.) Run <br>
```
  python3 -m uvicorn main:app --reload
```
3.) Login in Zomato using google chrome and while inspect find **sendJEvent** in Network-Fetch/XHR, Copy **Cookie & x-zomato-csrft** from Request Headers
<br>

<img width="1440" alt="Screenshot 2022-04-21 at 12 20 14 PM" src="https://user-images.githubusercontent.com/74853470/164391910-d9dba9c2-10c4-474c-bd97-326ec365972f.png">
<br>
4.) Use this endpoint with the values(Refer Point 3):- http://127.0.0.1:8000/zoltv/"x-zomato-csrft"?cookie="Cookie"
<br>
  Output:-<img width="258" alt="Screenshot 2022-04-21 at 12 24 54 PM" src="https://user-images.githubusercontent.com/74853470/164392691-de518697-6c3a-4713-a81a-253a74f78fed.png">
  And data.csv will also be created in the directory.
