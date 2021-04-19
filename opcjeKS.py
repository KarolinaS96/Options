import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd


class Binomial():
    def _init_(self, n, S, K, r, v, t, PutCall):
        #liczba krokow w modelu
        self.n=n
        #aktualna wartosc
        self.S=S
        #cena wykonania
        self.K=K
        #stopa risk-free
        self.r=r
        #zmiennosc
        self.v=v
        #w latach czas do wygasniecia
        self.t=t
        #typ put/call
        self.PutCall=PutCall
        
    def wycena(self):
        #krok 1 , czas 
        delta_t = self.t/self.n
        #wspolczynniki gora/dol 
        u=np.exp(self.v * np.sqrt(delta_t))
        d=np.exp(-self.v * np.sqrt(delta_t))
        #cofanie
        p=(np.exp(self.r * delta_t)-d)/(u-d)
        #print(p)
        
        #tworzenie macierzy z wartosciami akcji na dany moment
        akcje = np.zeros((self.n +1,self.n +1))
        akcje[0,0]=self.S
        for i in range (1, self.n + 1):
            #gora
            akcje[i,0]=akcje[i-1,0]*u
            #do dolu
            for j in range(1,i+1):
                akcje[i,j]=akcje[i-1,j-1]*d
        #print(akcje)
       #wycena na koncowych wezlach
        wartosc = np.zeros((self.n +1,self.n +1))
        for j in range(self.n +1):
           #call
           if self.PutCall == "C":
               wartosc[self.n,j]=max(0,akcje[self.n,j]-self.K)
               #put
           elif self.PutCall == "P":
               wartosc[self.n,j] = max(0, self.K - akcje[self.n,j])
        #print(wartosc)
        #algorytm backward od konca do poczatku wycena [dyskontowanie], max oplacalnosci
        for i in range(self.n - 1, -1, -1):
            for j in range(i + 1):
                if self.PutCall == "P":
                    wartosc[i, j] = max(0, self.K - akcje[i, j], 
                                        np.exp(-self.r * delta_t) * 
                                        (p * wartosc[i + 1, j] + (1 - p) * wartosc[i + 1, j + 1]))
                elif self.PutCall == "C":
                    wartosc[i, j] = max(0, akcje[i, j] - self.K, np.exp(-self.r * delta_t) * 
                                        (p * wartosc[i + 1, j] + (1 - p) * wartosc[i + 1, j + 1]))
        #print(wartosc)
        return round(wartosc[0,0],2)
        
    def wykres(self):
        if self.PutCall == "C":
            y = [-self.wycena()] * self.K
            y += [x - self.wycena() for x in range(self.K)]
            plt.plot(range(2 * self.K), y)
            plt.axis([0, 2 * self.K, min(y) - 10, max(y) + 10])
            plt.xlabel('Cena instrumentu bazowego')
            plt.ylabel('Zysk/strata')
            plt.axvline(x=self.S, linestyle='--', color='black')
            plt.axhline(y=0, linestyle=':', color='black')
            plt.title('Opcja amerykanska call')
            plt.text(self.S, 0, 'aktualnie')
            plt.show()
        elif self.PutCall == "P":
            y = [-x + self.K - self.wycena() for x in range(self.K)]
            y += [-self.wycena()] * (self.K)
            plt.plot(range(2 * self.K), y, color='red')
            plt.axis([0, 2 * self.K, min(y) - 10, max(y) + 10])
            plt.xlabel('Cena instrumentu bazowego')
            plt.ylabel('Zysk/strata')
            plt.axvline(x=self.S, linestyle='--', color='black')
            plt.axhline(y=0, linestyle=':', color='black')
            plt.title('Opcja amerykanska put')
            plt.text(self.S, 0, 'aktualnie')
            plt.show()
   






#test
for i in range(5):
    PutCall=random.choice(['P','C'])
    n=random.randint(4,40)
    S=random.randint(60,100)
    K=random.randint(60,100)
    r=random.uniform(0.0,1.0)
    v=random.uniform(0.0,1.0)
    t=random.uniform(1/12,10.0)
    opcja=Binomial()
    opcja.K=K
    opcja.PutCall=PutCall
    opcja.n=n
    opcja.S=S
    opcja.K=K
    opcja.r=r
    opcja.v=v
    opcja.t=t
    print(opcja.wycena()," typ ",PutCall)
    opcja.wykres()


#realny

djx=pd.read_csv("C:/",
                usecols=(0,1,11,12))
djx.insert(2,"wycena call",np.zeros(len(djx)),1)
djx=djx[['Expiration Date','Strike','Calls','wycena call','Puts']]
djx.insert(5,"wycena put",np.zeros(len(djx)),1)
Ex=djx['Expiration Date']
djx['Expiration Date']=(((pd.to_datetime(djx['Expiration Date'])-pd.datetime.today()).dt.days)/360)
djx['Strike']=djx['Strike'].astype('int32')
opcjaDJ=Binomial()
opcjaDJ.n=int(input("Wprowadz liczbe krokow w modelu: "))
opcjaDJ.r=0.083
opcjaDJ.v=0.1928
opcjaDJ.S=302.18


for i in range(len(djx)):
    opcjaDJ.K=djx.iloc[i]['Strike']
    opcjaDJ.t=djx.iloc[i]['Expiration Date']
    opcjaDJ.PutCall="C"
    djx.loc[i,("wycena call")]=opcjaDJ.wycena()
    opcjaDJ.PutCall="P"
    djx.loc[i,("wycena put")]=opcjaDJ.wycena()



djx['Expiration Date']=Ex
djx.to_excel(r'C:/djx_wycena.xlsx', index = False)


#print(djx.head(-15))

