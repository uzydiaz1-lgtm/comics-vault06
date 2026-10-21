# comics-vault06
es una pagina que se trata de comics, mangas, y escritores independiente 
 
 # PROYECTO-DJANGO2026 | Arquitectura MVT Multiapp

## 📌 Aclaración de Arquitectura y Nombres
El proyecto implementa una arquitectura **MVT Multiapp** dividida en dos aplicaciones principales:
1. **`comics` (App Cliente):** Destinada al usuario final, catálogo de cómics, lector, perfiles de usuario y búsquedas dinámicas. *(Corresponde conceptualmente a la app `cliente` adaptada a la temática de tienda de cómics)*.
2. **`administrador` (App Administrador):** Destinada al panel de gestión interna, control de inventario y bitácora de eventos operativos (`ReporteBitacora`).

---

## 🚀 Pasos para Instalación y Ejecución

### 1. Requisitos Previos
Asegurarse de contar con Python 3.10+ e instalar las dependencias en el entorno virtual.

### 2. Activación del Entorno Virtual (Windows PowerShell)
```powershell
.\virtual\Scripts\activate