# 📖 **README - no-local-net - Blockchain con Proof of Entanglement (PoE)**

## **Índice**
1. [Introducción](#introducción)
2. [¿Qué es la blockchain Proof of Entanglement (PoE)?](#qué-es-la-blockchain-proof-of-entanglement-poe)
3. [Características principales](#características-principales)
4. [Arquitectura del sistema](#arquitectura-del-sistema)
5. [Mecanismo de Consenso PoE](#mecanismo-de-consenso-poe)
6. [Módulos del código](#módulos-del-código)
7. [Instalación y uso](#instalación-y-uso)
8. [Contribuciones y contacto](#contribuciones-y-contacto)

---

## **Introducción**

Este proyecto implementa una **blockchain descentralizada** basada en el mecanismo de consenso **Proof of Entanglement (PoE)**, desarrollado en **Python** utilizando **FastAPI**. A diferencia de otros protocolos tradicionales como **Proof of Work (PoW)** y **Proof of Stake (PoS)**, PoE utiliza **entrelazamientos criptográficos** entre nodos y bloques para garantizar la seguridad de la red.

La blockchain soporta la ejecución de **contratos inteligentes escritos en Python**, lo que permite una integración eficiente y segura de operaciones descentralizadas.

---

## **¿Qué es la blockchain Proof of Entanglement (PoE)?**

### 🔹 **Definición**

Proof of Entanglement (**PoE**) es un innovador mecanismo de consenso basado en la creación de entrelazamientos entre los nodos y bloques dentro de la blockchain. En lugar de depender de la minería (PoW) o de validadores con grandes cantidades de tokens (PoS), PoE valida la seguridad de la red a través de la interconexión de datos entre nodos y bloques.

### 🔹 **¿Cómo funciona?**

1. **Entrelazamiento de Nodos y Bloques**: Los nodos se entrelazan entre sí, y los bloques generan entrelazamientos con bloques de coherencia.
2. **Generación de Claves de Coherencia**: Un bloque de coherencia genera una **coherence key**.
3. **Predicción de Validación**: Los nodos generan predicciones basadas en sus **entanglement keys** y las de su nodo entrelazado.
4. **Cálculo del Hash de Predicción**: Cada nodo hashea su predicción usando su clave y la del nodo entrelazado.
5. **Comparación con la Coherence Key**: El consenso se alcanza eligiendo la predicción que más se asemeje al resultado del hasheo de la **coherence key**.
6. **Validación del Bloque**: Si la predicción es lo suficientemente precisa, el bloque se valida y se agrega a la blockchain.

---

## **Características principales**

- ✅ **Mecanismo de consenso PoE**: Seguro y eficiente, sin necesidad de una gran potencia computacional.
- ✅ **Contratos inteligentes en Python**: Ejecutados en un entorno de máquina virtual controlado.
- ✅ **Soporte para tokens y NFTs**: Implementación de estándares inspirados en ERC-20 y ERC-721.
- ✅ **Alta seguridad e inmutabilidad**: Gracias a los entrelazamientos criptográficos.

---

## **Arquitectura del sistema**

### 📌 **1. Nodo Blockchain**
Cada nodo en la red almacena la cadena de bloques y participa en la validación de los bloques a través de PoE.

### 📌 **2. Validación con PoE**
Los nodos verifican la integridad de los bloques asegurando que su entrelazamiento con otros nodos y bloques sea válido.

### 📌 **3. Contratos Inteligentes**
Los contratos inteligentes se ejecutan en un entorno aislado y controlado basado en Python.

### 📌 **4. Tokens y NFTs**
Implementación de clases de tokens y NFTs, siguiendo modelos similares a ERC-20 y ERC-721.

---

## **Mecanismo de Consenso PoE**

El protocolo PoE utiliza predicciones y validaciones basadas en entrelazamientos criptográficos. Su funcionamiento es el siguiente:

1. **Cada nodo tiene una Entanglement Key**: Una clave única vinculada a otro nodo de la red.
2. **Los bloques de coherencia generan una Coherence Key**: Esta clave se utiliza para la validación de bloques.
3. **Generación de predicciones**: Cada nodo genera una predicción basada en su Entanglement Key y la del nodo entrelazado.
4. **Hash de las predicciones**: Las predicciones generadas son hasheadas con las claves correspondientes y comparadas con la Coherence Key hasheada.
5. **Consenso**: Se alcanza el consenso seleccionando la predicción que más se aproxime al resultado del hash de la Coherence Key.
6. **Validación del bloque**: Si la predicción es válida, el bloque se agrega a la blockchain.

Este sistema garantiza la seguridad de la red sin depender de grandes recursos computacionales o tokens en staking.

---

## **Módulos del código**

- 📂 `core/` - Implementación del protocolo blockchain y PoE.
- 📂 `smart_contracts/` - Ejecución de contratos inteligentes.
- 📂 `network/` - Comunicación entre nodos.
- 📂 `wallet/` - Gestión de claves públicas y privadas.

---

## **Instalación y uso**

```bash
# Clonar el repositorio
git clone https://github.com/antsegang/no-local-net.git
cd no-local-net

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar un nodo
uvicorn app:app --port 5000
```

---

## **Contribuciones y contacto**

Si deseas contribuir a este proyecto, por favor contacta a:

📧 **absegura@no-local-net.ecolatam.com**  
🌐 **https://no-local-net.ecolatam.com**

Para más detalles sobre la licencia, consulta el archivo **LICENSE.md**.