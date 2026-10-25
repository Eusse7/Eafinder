# Backlog de Historias de Usuario — EAFinder

> Historias de usuario estructuradas a partir del backlog proporcionado. Los criterios describen el comportamiento esperado y pueden ajustarse a las reglas definitivas del producto.

## Índice

- [US01 — Consulta en lenguaje natural de la normativa](#us01-consulta-en-lenguaje-natural-de-la-normativa)
- [US02 — Entrenamiento y actualización de la base de conocimiento](#us02-entrenamiento-y-actualizacion-de-la-base-de-conocimiento)
- [US03 — Acceso mediante una interfaz centralizada](#us03-acceso-mediante-una-interfaz-centralizada)
- [US04 — Consulta de procedimientos del reglamento académico](#us04-consulta-de-procedimientos-del-reglamento-academico)
- [US05 — Panel de analítica de búsquedas](#us05-panel-de-analitica-de-busquedas)
- [US06 — Interfaz de chat adaptable a diferentes pantallas](#us06-interfaz-de-chat-adaptable-a-diferentes-pantallas)
- [US07 — Indicador de estado de procesamiento](#us07-indicador-de-estado-de-procesamiento)
- [US08 — Procesamiento de consultas en lenguaje natural](#us08-procesamiento-de-consultas-en-lenguaje-natural)
- [US09 — Citación de fuentes institucionales](#us09-citacion-de-fuentes-institucionales)
- [US10 — Control de respuestas fuera del dominio](#us10-control-de-respuestas-fuera-del-dominio)
- [US11 — Manejo de errores de conexión](#us11-manejo-de-errores-de-conexion)
- [US12 — Carga de nuevos reglamentos](#us12-carga-de-nuevos-reglamentos)
- [US13 — Actualización o eliminación de documentos obsoletos](#us13-actualizacion-o-eliminacion-de-documentos-obsoletos)
- [US-14 — Entrada de voz para consultas](#us14-entrada-de-voz-para-consultas)
- [US15 — Valoración de la precisión de las respuestas](#us15-valoracion-de-la-precision-de-las-respuestas)
- [US16 — Sugerencias de preguntas frecuentes](#us16-sugerencias-de-preguntas-frecuentes)
- [US-17 — Integración con el calendario académico](#us17-integracion-con-el-calendario-academico)
- [US-18 — Registro de consultas sin respuesta y alertas de brechas de conocimiento](#us18-registro-de-consultas-sin-respuesta-y-alertas-de-brechas-de-conocimiento)
- [US19 — Cambio entre tema claro y oscuro](#us19-cambio-entre-tema-claro-y-oscuro)
- [US20 — Filtro de seguridad y moderación de contenido sensible](#us20-filtro-de-seguridad-y-moderacion-de-contenido-sensible)

### US01 - Consulta en lenguaje natural de la normativa
**Como** Estudiante o usuario de EAFIT  
**Quiero** consultar reglamentos institucionales mediante preguntas en lenguaje natural  
**Para** obtener información normativa sin tener que buscar manualmente en documentos extensos

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Consulta válida
  * **Dado que** el usuario se encuentra en la interfaz de EAFinder
  * **Cuando** formula una pregunta sobre una normativa institucional incluida en la base de conocimiento
  * **Entonces** el sistema presenta una respuesta pertinente basada en la información disponible
* **Escenario 2:** Pregunta ambigua
  * **Dado que** el usuario formula una pregunta que puede tener varios significados
  * **Cuando** envía la pregunta
  * **Entonces** el sistema solicita una aclaración o responde indicando la interpretación utilizada

### US02 - Entrenamiento y actualización de la base de conocimiento
**Como** Administrador del sistema  
**Quiero** mantener entrenada y actualizada la base de conocimiento institucional  
**Para** ofrecer respuestas alineadas con la documentación vigente de EAFIT

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Documento incorporado
  * **Dado que** existe un documento institucional válido y autorizado
  * **Cuando** el administrador lo incorpora al proceso de actualización
  * **Entonces** el contenido queda disponible para las consultas una vez finaliza el procesamiento
* **Escenario 2:** Error de procesamiento
  * **Dado que** se intenta procesar un documento inválido o ilegible
  * **Cuando** el sistema procesa el archivo
  * **Entonces** se informa el error y el documento no se incorpora como contenido válido

### US03 - Acceso mediante una interfaz centralizada
**Como** Usuario de EAFIT  
**Quiero** acceder al chatbot desde una interfaz centralizada  
**Para** consultar información institucional desde un único lugar

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Acceso a la interfaz
  * **Dado que** el usuario dispone de un navegador compatible
  * **Cuando** abre la plataforma EAFinder
  * **Entonces** se muestra la interfaz principal y los controles necesarios para realizar consultas
* **Escenario 2:** Uso de la interfaz
  * **Dado que** la interfaz principal está disponible
  * **Cuando** el usuario escribe una pregunta y la envía
  * **Entonces** la consulta se procesa y la respuesta se muestra en la misma interfaz

### US04 - Consulta de procedimientos del reglamento académico
**Como** Estudiante de EAFIT  
**Quiero** consultar los pasos y requisitos de procedimientos académicos  
**Para** comprender cómo realizar trámites académicos de acuerdo con la normativa

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Procedimiento documentado
  * **Dado que** la base de conocimiento contiene información sobre el procedimiento consultado
  * **Cuando** el estudiante pregunta cómo realizarlo
  * **Entonces** el sistema explica los pasos y requisitos respaldados por la documentación
* **Escenario 2:** Procedimiento no encontrado
  * **Dado que** la base de conocimiento no contiene información suficiente sobre el procedimiento
  * **Cuando** el estudiante realiza la consulta
  * **Entonces** el sistema comunica que no dispone de información suficiente y evita inventar pasos

### US05 - Panel de analítica de búsquedas
**Como** Administrador o equipo del proyecto  
**Quiero** visualizar métricas agregadas de las consultas realizadas  
**Para** identificar patrones de uso y oportunidades de mejora del chatbot

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Visualización de métricas
  * **Dado que** existen registros de consultas y el panel está habilitado
  * **Cuando** el administrador abre el panel
  * **Entonces** se muestran métricas disponibles, como volumen de consultas y temas frecuentes
* **Escenario 2:** Sin datos registrados
  * **Dado que** no existen consultas registradas para el periodo seleccionado
  * **Cuando** el administrador consulta el panel
  * **Entonces** el sistema muestra un estado vacío claro sin presentar métricas ficticias

### US06 - Interfaz de chat adaptable a diferentes pantallas
**Como** Usuario de EAFIT  
**Quiero** utilizar el chat desde dispositivos de distintos tamaños  
**Para** consultar información con una experiencia legible y fácil de usar

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Pantalla de escritorio
  * **Dado que** el usuario abre EAFinder desde un computador
  * **Cuando** accede al chat
  * **Entonces** los mensajes, el campo de entrada y los controles se muestran correctamente
* **Escenario 2:** Pantalla móvil
  * **Dado que** el usuario abre EAFinder desde un dispositivo móvil
  * **Cuando** accede al chat y escribe una consulta
  * **Entonces** la interfaz se adapta al tamaño de pantalla sin ocultar controles esenciales ni requerir desplazamiento horizontal

### US07 - Indicador de estado de procesamiento
**Como** Usuario de EAFIT  
**Quiero** ver el estado mientras se procesa una consulta  
**Para** saber que el sistema está trabajando y evitar enviar repetidamente la misma pregunta

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Consulta en proceso
  * **Dado que** el usuario ha enviado una consulta y el sistema aún no ha respondido
  * **Cuando** comienza el procesamiento
  * **Entonces** la interfaz muestra un indicador visible de carga o procesamiento
* **Escenario 2:** Respuesta recibida
  * **Dado que** el sistema termina de procesar la consulta
  * **Cuando** la respuesta queda disponible
  * **Entonces** el indicador de procesamiento desaparece y se muestra la respuesta

### US08 - Procesamiento de consultas en lenguaje natural
**Como** Usuario de EAFIT  
**Quiero** formular preguntas con palabras y expresiones cotidianas  
**Para** recibir respuestas sin tener que usar comandos o palabras clave exactas

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Pregunta con lenguaje cotidiano
  * **Dado que** el sistema está disponible y la pregunta se relaciona con información institucional
  * **Cuando** el usuario envía la pregunta en lenguaje natural
  * **Entonces** el sistema interpreta la intención y genera una respuesta relevante
* **Escenario 2:** Consulta incompleta
  * **Dado que** la pregunta no contiene contexto suficiente para responder con fiabilidad
  * **Cuando** el usuario envía la consulta
  * **Entonces** el sistema solicita información adicional o explica qué dato necesita

### US09 - Citación de fuentes institucionales
**Como** Usuario de EAFIT  
**Quiero** consultar las fuentes institucionales que respaldan una respuesta  
**Para** verificar la información y localizar el documento de origen

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Respuesta con respaldo
  * **Dado que** la respuesta se genera a partir de documentos institucionales identificables
  * **Cuando** el sistema presenta la respuesta
  * **Entonces** incluye referencias o citas a las fuentes utilizadas cuando están disponibles
* **Escenario 2:** Fuente no identificable
  * **Dado que** el sistema no puede identificar una fuente concreta que respalde la respuesta
  * **Cuando** genera una respuesta
  * **Entonces** no inventa nombres de documentos ni referencias y comunica la limitación cuando corresponda

### US10 - Control de respuestas fuera del dominio
**Como** Usuario de EAFIT  
**Quiero** recibir una indicación cuando pregunta algo fuera del alcance institucional del chatbot  
**Para** evitar respuestas inventadas o ajenas al propósito de EAFinder

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Pregunta fuera del dominio
  * **Dado que** el usuario formula una pregunta no relacionada con la información institucional cubierta
  * **Cuando** envía la pregunta
  * **Entonces** el sistema indica respetuosamente que la consulta está fuera de su alcance y orienta al usuario hacia temas admitidos
* **Escenario 2:** Pregunta parcialmente relacionada
  * **Dado que** la consulta mezcla un tema institucional con otro no cubierto
  * **Cuando** envía la pregunta
  * **Entonces** el sistema responde únicamente la parte que puede fundamentar y aclara las limitaciones

### US11 - Manejo de errores de conexión
**Como** Usuario de EAFIT  
**Quiero** recibir información clara cuando ocurre un error de conexión  
**Para** comprender el problema y saber cuándo puede volver a intentarlo

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Falla de conexión
  * **Dado que** el usuario intenta enviar una consulta y el servicio no está disponible
  * **Cuando** envía la pregunta
  * **Entonces** la interfaz muestra un mensaje de error comprensible y sugiere intentarlo nuevamente
* **Escenario 2:** Recuperación del servicio
  * **Dado que** la conexión vuelve a estar disponible después de un error
  * **Cuando** el usuario vuelve a enviar la consulta
  * **Entonces** el sistema permite continuar y muestra la respuesta si el procesamiento finaliza correctamente

### US12 - Carga de nuevos reglamentos
**Como** Administrador del sistema  
**Quiero** cargar nuevos documentos normativos autorizados  
**Para** mantener actualizada la información que utiliza el chatbot

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Carga exitosa
  * **Dado que** el administrador dispone de un documento permitido y compatible
  * **Cuando** selecciona y carga el documento
  * **Entonces** el sistema valida el archivo, confirma la recepción y lo procesa para incorporarlo a la base de conocimiento
* **Escenario 2:** Archivo no válido
  * **Dado que** el archivo no cumple el formato o las condiciones permitidas
  * **Cuando** el administrador intenta cargarlo
  * **Entonces** el sistema rechaza el archivo e informa el motivo sin incorporarlo a la base de conocimiento

### US13 - Actualización o eliminación de documentos obsoletos
**Como** Administrador del sistema  
**Quiero** actualizar o retirar documentos que ya no están vigentes  
**Para** evitar que el chatbot responda con información institucional desactualizada

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Actualización de documento
  * **Dado que** existe un documento que ha sido reemplazado por una versión vigente
  * **Cuando** el administrador carga la nueva versión y confirma la actualización
  * **Entonces** la versión vigente queda disponible y la versión obsoleta deja de utilizarse para responder
* **Escenario 2:** Retiro de documento
  * **Dado que** un documento ya no debe utilizarse como fuente
  * **Cuando** el administrador solicita retirarlo
  * **Entonces** el documento deja de estar disponible para nuevas consultas y el sistema confirma la operación

### US-14 - Entrada de voz para consultas
**Como** Usuario de EAFIT  
**Quiero** dictar una pregunta mediante el micrófono  
**Para** realizar consultas sin tener que escribirlas manualmente

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Dictado reconocido
  * **Dado que** el navegador admite el uso del micrófono y el usuario concede permiso
  * **Cuando** activa la entrada de voz y dicta una pregunta
  * **Entonces** el sistema convierte el audio en texto visible para que el usuario pueda enviarlo
* **Escenario 2:** Permiso denegado o voz no reconocida
  * **Dado que** el usuario no concede permiso al micrófono o no se reconoce el audio
  * **Cuando** intenta dictar una consulta
  * **Entonces** la interfaz informa que no fue posible reconocer la voz y permite escribir la pregunta

### US15 - Valoración de la precisión de las respuestas
**Como** Usuario de EAFIT  
**Quiero** calificar una respuesta con pulgar arriba o pulgar abajo  
**Para** ayudar a identificar respuestas útiles y oportunidades de mejora

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Valoración positiva
  * **Dado que** el sistema ha mostrado una respuesta
  * **Cuando** el usuario selecciona pulgar arriba
  * **Entonces** la valoración queda registrada y la interfaz confirma la acción
* **Escenario 2:** Valoración negativa
  * **Dado que** el sistema ha mostrado una respuesta
  * **Cuando** el usuario selecciona pulgar abajo
  * **Entonces** la valoración queda registrada como retroalimentación negativa
* **Escenario 3:** Evitar registros duplicados
  * **Dado que** el usuario ya ha valorado una respuesta
  * **Cuando** vuelve a seleccionar una valoración
  * **Entonces** el sistema aplica la regla definida para actualizar o conservar la valoración sin generar registros duplicados indebidos

### US16 - Sugerencias de preguntas frecuentes
**Como** Usuario de EAFIT  
**Quiero** ver sugerencias de preguntas frecuentes o ejemplos de consulta  
**Para** empezar una conversación rápidamente y conocer qué puede preguntar

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Sugerencias visibles
  * **Dado que** el usuario abre la interfaz de chat
  * **Cuando** la interfaz termina de cargar
  * **Entonces** se muestran sugerencias de preguntas relevantes y comprensibles
* **Escenario 2:** Seleccionar sugerencia
  * **Dado que** se muestran preguntas sugeridas
  * **Cuando** el usuario selecciona una sugerencia
  * **Entonces** el texto se incorpora al campo de consulta o se envía según el comportamiento definido por la interfaz

### US-17 — Integración con el calendario académico y plazos reglamentarios
**Como** Estudiante  
**Quiero** consultar los plazos y términos oficiales establecidos en el Reglamento Académico (ej. semestres máximos permitidos, días para apelar una calificación o decisión disciplinaria)  
**Para** comprender mis derechos y obligaciones reglamentarias sin tener que leer todo el documento  

#### Criterios de Aceptación:
* El sistema responde preguntas sobre plazos y límites de tiempo utilizando exclusivamente el texto del Reglamento Académico (ej. "3 días hábiles").
* Si un usuario pregunta por fechas dinámicas del calendario académico (ej. "¿Cuándo inician clases en 2026?"), el sistema responde aclarando que únicamente gestiona normas reglamentarias y no el calendario académico.
* Las respuestas sobre plazos y términos deben citar explícitamente el artículo exacto que fija dicho límite.

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Consulta de plazos y términos reglamentarios
  * **Dado que** un estudiante pregunta "¿Cuántos días tengo para apelar una decisión disciplinaria?" (o sobre un término o plazo reglamentario similar)
  * **Cuando** el sistema recupera la información de la base de conocimiento
  * **Entonces** proporciona el plazo exacto establecido en el reglamento, cita explícitamente el artículo correspondiente y advierte que no gestiona fechas específicas de calendario
* **Escenario 2:** Consulta de fechas dinámicas del calendario académico
  * **Dado que** un usuario pregunta por una fecha dinámica del calendario académico (ej. "¿Cuándo inician las clases en 2026?", fechas de receso o pagos)
  * **Cuando** el sistema procesa la consulta
  * **Entonces** responde indicando que solo gestiona normas reglamentarias y no el calendario académico dinámico, sugiriendo consultar los canales oficiales (Autoservicio EPIK o web EAFIT)

### US-18 - Registro de consultas sin respuesta y alertas de brechas de conocimiento
**Como** Administrador o equipo de conocimiento  
**Quiero** identificar preguntas que el chatbot no pudo responder  
**Para** detectar vacíos de información y priorizar mejoras de la base de conocimiento

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Consulta sin respuesta
  * **Dado que** el sistema no encuentra información suficiente para responder una consulta
  * **Cuando** finaliza el intento de respuesta
  * **Entonces** se registra el evento con los datos necesarios para analizar la brecha, respetando las reglas de privacidad definidas
* **Escenario 2:** Revisión de brechas
  * **Dado que** existen consultas sin respuesta registradas
  * **Cuando** el administrador revisa el reporte
  * **Entonces** puede identificar las consultas recurrentes que requieren revisar o ampliar la base de conocimiento

### US19 - Cambio entre tema claro y oscuro
**Como** Usuario de EAFIT  
**Quiero** cambiar la apariencia entre tema claro y tema oscuro  
**Para** usar la plataforma según sus preferencias visuales y condiciones de iluminación

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Activar tema oscuro
  * **Dado que** la interfaz está en tema claro
  * **Cuando** el usuario activa el control de tema
  * **Entonces** la interfaz cambia al tema oscuro y mantiene legibles los textos y controles
* **Escenario 2:** Activar tema claro
  * **Dado que** la interfaz está en tema oscuro
  * **Cuando** el usuario selecciona tema claro
  * **Entonces** la interfaz cambia al tema claro y conserva el contenido y el estado de la conversación

### US20 - Filtro de seguridad y moderación de contenido sensible
**Como** Usuario de EAFIT  
**Quiero** interactuar con un chatbot que aplica controles de seguridad y moderación  
**Para** reducir respuestas inapropiadas, riesgosas o relacionadas con contenido sensible fuera del propósito institucional

#### Criterios de Aceptación (Gherkin / Escenarios):
* **Escenario 1:** Solicitud no permitida
  * **Dado que** el usuario envía una solicitud que activa las reglas de moderación configuradas
  * **Cuando** el sistema evalúa la solicitud
  * **Entonces** el sistema se abstiene de proporcionar contenido no permitido y ofrece una respuesta segura cuando sea posible
* **Escenario 2:** Consulta institucional legítima
  * **Dado que** el usuario realiza una consulta institucional permitida que no infringe las reglas de seguridad
  * **Cuando** envía la pregunta
  * **Entonces** el sistema procesa la consulta normalmente sin bloquearla de manera injustificada
