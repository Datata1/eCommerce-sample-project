package main

import (
	"fmt" // Importiert für die String-Formatierung
	"net/http"
	"os" // Importiert für den Zugriff auf Environment-Variablen

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	e := echo.New()

	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	e.GET("/hello", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"message": "Hallo vom Go Echo API-Service!",
		})
	})

	port := os.Getenv("GO_PORT")
	if port == "" {
		port = "8080"
	}

	addr := fmt.Sprintf("0.0.0.0:%s", port)
	e.Logger.Infof("Server wird auf Adresse %s gestartet", addr) // Nützliches Logging

	e.Logger.Fatal(e.Start(addr))
}