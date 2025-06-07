package main

import (
	"net/http"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger()) 
	e.Use(middleware.Recover()) 

	e.GET("/api/hello", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"message": "Hallo vom Go Echo API-Service!",
		})
	})
	e.Logger.Fatal(e.Start("0.0.0.0:8080"))
}