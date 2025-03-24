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

Este proyecto implementa una **blockchain descentralizada** basada en un novedoso mecanismo de consenso llamado **Proof of Entanglement (PoE)**, desarrollado en **Python** usando **FastAPI**. A diferencia de los modelos tradicionales como **Proof of Work (PoW)** y **Proof of Stake (PoS)**, el protocolo PoE introduce un método basado en **entrelazamientos criptográficos** entre nodos y bloques para validar la seguridad de la red.

Esta blockchain está diseñada para soportar **contratos inteligentes escritos en Python**, asegurando eficiencia y seguridad en la ejecución de operaciones descentralizadas.

---

## **¿Qué es la blockchain Proof of Entanglement (PoE)?**

### 🔹 **Definición**

Proof of Entanglement (**PoE**) es un mecanismo de consenso basado en la creación de entrelazamientos entre los nodos y los bloques dentro de la blockchain. En lugar de depender de minería intensiva (como PoW) o de validadores con grandes cantidades de tokens (como PoS), PoE garantiza la seguridad de la red a través de la interconexión de datos dentro de la cadena.

### 🔹 **¿Cómo funciona?**

1. **Entrelazamiento de Nodos y Bloques:** Los nodos se entrelazan entre sí, y los bloques generan entrelazamientos con bloques de coherencia.
2. **Generación de Claves de Coherencia:** Un bloque de coherencia genera una **coherence key**.
3. **Predicción de Validación:** Los nodos generan predicciones basadas en sus **entanglement keys** y las de su pareja entrelazada.
4. **Cálculo del Hash de Predicción:** La predicción de cada nodo se hashea utilizando su propia clave y la de su nodo entrelazado.
5. **Comparación con la Coherence Key:** El consenso se logra eligiendo la predicción que más se aproxime al resultado del hasheo de la **coherence key**.
6. **Validación del Bloque:** Si una predicción se acerca lo suficiente a la coherence key hasheada, el bloque es validado y agregado a la blockchain.

---

## **Características principales**

- ✅ **Mecanismo de consenso PoE** (seguro y eficiente sin necesidad de alta potencia de cómputo).
- ✅ **Contratos inteligentes en Python** (ejecutados en un entorno de máquina virtual controlado).
- ✅ **Soporte para tokens y NFTs** (compatibles con estándares inspirados en ERC-20 y ERC-721).
- ✅ **Alta seguridad e inmutabilidad** gracias a los entrelazamientos criptográficos.

---

## **Arquitectura del sistema**

### 📌 **1. Nodo Blockchain**
Cada nodo en la red almacena la cadena de bloques y participa en el proceso de validación de bloques a través de PoE.

### 📌 **2. Validación con PoE**
Los nodos verifican la integridad de un bloque asegurando que su entrelazamiento con otros nodos y bloques sea válido.

### 📌 **3. Contratos Inteligentes**
Los contratos son ejecutados en un entorno aislado basado en Python.

### 📌 **4. Tokens y NFTs**
Implementación de clases basadas en modelos similares a ERC-20 y ERC-721.

---

## **Mecanismo de Consenso PoE**

El protocolo PoE se basa en la predicción y validación de coherencia mediante entrelazamientos criptográficos. Su proceso es el siguiente:

1. **Cada nodo tiene una Entanglement Key**, la cual está ligada a otro nodo en la red.
2. **Los bloques de coherencia generan una Coherence Key**, utilizada como referencia para la validación.
3. **Cada nodo genera una predicción** basada en su Entanglement Key y la de su nodo entrelazado.
4. **Las predicciones de los nodos son hasheadas** con sus claves y comparadas con la Coherence Key hasheada.
5. **El consenso se logra** eligiendo la predicción más cercana al resultado del hasheo de la Coherence Key.
6. **Si una predicción es válida**, el bloque es agregado a la blockchain.

Este método garantiza que la seguridad de la red dependa del correcto entrelazamiento de datos en lugar de la potencia de cómputo o el staking de tokens.

---

## **Módulos del código**

📂 `core/` - Implementación del protocolo blockchain y PoE.  
📂 `smart_contracts/` - Ejecución de contratos inteligentes.  
📂 `network/` - Comunicación entre nodos.  
📂 `wallet/` - Generación y gestión de claves públicas y privadas.  

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

Para más información sobre la licencia, revisa el archivo **LICENSE.md**.

---