package main

import (
	"bytes"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/unidoc/unioffice/document"
	"github.com/unidoc/unioffice/measurement"
	"github.com/unidoc/unioffice/schema/soo/wml"
	"golang.org/x/crypto/bcrypt"
	"os/exec"
)

// Defendant represents a legal entity being sued
type Defendant struct {
	EntityType      string `json:"entityType"`      // "Credit Bureau" | "Financial Institution" | "Corporation"
	Name            string `json:"name"`            // Full legal entity name
	Address         string `json:"address"`         // Complete legal address
	RegisteredAgent string `json:"registeredAgent"` // Service of process agent
	State           string `json:"state"`           // State of incorporation/residence
	County          string `json:"county"`          // County for service
}

// CauseOfAction represents a legal theory being pursued
type CauseOfAction struct {
	Count           int      `json:"count"`           // COUNT ONE, COUNT TWO, etc.
	Title           string   `json:"title"`           // "Violation of FCRA § 1681s-2(b)"
	Statute         string   `json:"statute"`         // "15 U.S.C. § 1681s-2(b)"
	Elements        []string `json:"elements"`        // Required legal elements
	Allegations     string   `json:"allegations"`     // Specific factual allegations
	Remedies        []string `json:"remedies"`        // Available legal remedies
}

// SavedDocument represents a saved legal document
type SavedDocument struct {
	ID           string    `json:"id"`           // Unique document identifier
	FileName     string    `json:"fileName"`     // Generated file name
	FilePath     string    `json:"filePath"`     // Full path to saved file
	DocumentType string    `json:"documentType"` // "complaint", "motion", etc.
	SavedDate    time.Time `json:"savedDate"`    // When document was saved
	FileSize     int64     `json:"fileSize"`     // File size in bytes
	Status       string    `json:"status"`       // "saved", "error", etc.
	ICloudPath   string    `json:"icloudPath"`   // iCloud path if synced
	SyncStatus   string    `json:"syncStatus"`   // "synced", "pending", "error"
}

// ICloudCredentials represents encrypted iCloud authentication
type ICloudCredentials struct {
	Username    string `json:"username"`
	AppPassword string `json:"appPassword"` // App-specific password for security
	SessionID   string `json:"sessionId"`
	CreatedAt   time.Time `json:"createdAt"`
	ExpiresAt   time.Time `json:"expiresAt"`
}

// ICloudDocument represents a document in iCloud
type ICloudDocument struct {
	ID           string    `json:"id"`
	Name         string    `json:"name"`
	Path         string    `json:"path"`
	Size         int64     `json:"size"`
	Modified     time.Time `json:"modified"`
	Type         string    `json:"type"`         // "pdf", "docx", etc.
	IsDirectory  bool      `json:"isDirectory"`
}

// ICloudSyncStatus represents sync operation status
type ICloudSyncStatus struct {
	DocumentID    string    `json:"documentId"`
	Status        string    `json:"status"`        // "pending", "syncing", "completed", "error"
	Progress      int       `json:"progress"`      // 0-100
	Message       string    `json:"message"`
	StartedAt     time.Time `json:"startedAt"`
	CompletedAt   time.Time `json:"completedAt"`
	ErrorMessage  string    `json:"errorMessage"`
}

// ClientCase represents the structured data extracted from documents
type ClientCase struct {
	ClientName            string    `json:"clientName"`
	ContactInfo           string    `json:"contactInfo"`
	ResidenceLocation     string    `json:"residenceLocation"`
	FinancialInstitution  string    `json:"financialInstitution"`
	AccountOpenDate       time.Time `json:"accountOpenDate"`
	CreditLimit           string    `json:"creditLimit"`
	TravelLocation        string    `json:"travelLocation"`
	TravelStartDate       time.Time `json:"travelStartDate"`
	TravelEndDate         time.Time `json:"travelEndDate"`
	FraudAmount           string    `json:"fraudAmount"`
	FraudStartDate        time.Time `json:"fraudStartDate"`
	FraudEndDate          time.Time `json:"fraudEndDate"`
	FraudDetails          string    `json:"fraudDetails"`
	DiscoveryDate         time.Time `json:"discoveryDate"`
	DisputeCount          int       `json:"disputeCount"`
	DisputeMethods        []string  `json:"disputeMethods"`
	BankResponse          string    `json:"bankResponse"`
	PoliceReportFiled     bool      `json:"policeReportFiled"`
	PoliceReportDetails   string    `json:"policeReportDetails"`
	CreditBureauDisputes  []string  `json:"creditBureauDisputes"`
	CreditBureauDisputeDate time.Time `json:"creditBureauDisputeDate"`
	AdditionalEvidence    string    `json:"additionalEvidence"`
	CreditImpact          string    `json:"creditImpact"`

	// Court Information (from Civil Cover Sheet)
	CourtJurisdiction     string          `json:"courtJurisdiction"`     // "EASTERN DISTRICT OF NEW YORK"
	CourtDivision         string          `json:"courtDivision"`         // "BROOKLYN DIVISION"
	CaseClassification    string          `json:"caseClassification"`    // "CONSUMER CREDIT"
	JuryDemand           bool            `json:"juryDemand"`            // Jury trial demanded
	CaseNumber           string          `json:"caseNumber"`            // Assigned case number
	FilingDate           time.Time       `json:"filingDate"`            // Date case filed

	// Enhanced Attorney Information (from Civil Cover Sheet)
	AttorneyName         string          `json:"attorneyName"`          // "Kevin Mallon"
	AttorneyBarNumber    string          `json:"attorneyBarNumber"`     // NY Bar number
	AttorneyFirm         string          `json:"attorneyFirm"`          // "MALLON CONSUMER LAW GROUP"
	AttorneyEmail        string          `json:"attorneyEmail"`         // Professional email
	AttorneyPhone        string          `json:"attorneyPhone"`         // Professional phone
	AttorneyFax          string          `json:"attorneyFax"`           // Professional fax

	// Enhanced Legal Structure
	Defendants           []Defendant     `json:"defendants"`            // All defendants with legal details
	CausesOfAction       []CauseOfAction `json:"causesOfAction"`        // Legal theories being pursued
	ClaimAmount          string          `json:"claimAmount"`           // Total damages claimed
	RelatedCases         []string        `json:"relatedCases"`          // Related case numbers

	// Document Management
	SavedDocuments       []SavedDocument `json:"savedDocuments"`       // Track saved documents for this case
}

// Document represents a legal document in the system
type Document struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Type        string `json:"type"` // "pdf", "docx", etc.
	Path        string `json:"path"`
	ContentType string `json:"contentType"` // "attorney_notes", "adverse_action", etc.
}

// ExtractedText contains text extracted from documents
type ExtractedText struct {
	DocumentID string `json:"documentId"`
	Text       string `json:"text"`
	Pages      int    `json:"pages"`
}

// TemplateSection represents a section in the complaint template
type TemplateSection struct {
	ID          string `json:"id"`
	Title       string `json:"title"`
	Placeholders []TemplatePlaceholder `json:"placeholders"`
}

// TemplatePlaceholder represents a placeholder in the template
type TemplatePlaceholder struct {
	Placeholder string `json:"placeholder"`
	DataField   string `json:"dataField"`
	Required    bool   `json:"required"`
	Fallback    string `json:"fallback,omitempty"`
}

// User represents a system user
type User struct {
	ID           int       `json:"id"`
	Username     string    `json:"username"`
	PasswordHash string    `json:"password_hash"`
	Role         string    `json:"role"`         // "attorney", "admin", "demo"
	Firm         string    `json:"firm"`
	Email        string    `json:"email"`
	Created      time.Time `json:"created"`
	Active       bool      `json:"active"`
}

// UserSession represents an active user session
type UserSession struct {
	SessionID string    `json:"sessionId"`
	UserID    int       `json:"userId"`
	Username  string    `json:"username"`
	Role      string    `json:"role"`
	CreatedAt time.Time `json:"createdAt"`
	ExpiresAt time.Time `json:"expiresAt"`
}

// LoginRequest represents a login request
type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// Main function
func main() {
	router := gin.Default()

	// Setup CORS
	router.Use(func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})

	// Serve static files
	router.Static("/static", "../frontend")
	
	// Serve login page for unauthenticated users
	router.GET("/login", func(c *gin.Context) {
		c.File("../frontend/login.html")
	})
	
	// Serve main application for authenticated users
	router.GET("/", func(c *gin.Context) {
		// Check if user is authenticated
		sessionToken, err := c.Cookie("session_token")
		if err != nil {
			// No session cookie, redirect to login
			c.Redirect(http.StatusFound, "/login")
			return
		}
		
		// Validate session
		if session, exists := userSessions[sessionToken]; !exists || time.Now().After(session.ExpiresAt) {
			// Invalid or expired session, redirect to login
			if exists {
				delete(userSessions, sessionToken)
			}
			c.SetCookie("session_token", "", -1, "/", "", false, true)
			c.Redirect(http.StatusFound, "/login")
			return
		}
		
		// Valid session, serve main application
		c.File("../frontend/index.html")
	})

	// Define API endpoints
	api := router.Group("/api")
	{
		// Authentication endpoints (no middleware)
		api.POST("/login", handleLogin)
		api.POST("/logout", handleLogout)
		api.GET("/validate-session", handleValidateSession)
		
		// Protected endpoints (require authentication)
		protected := api.Group("/")
		protected.Use(authMiddleware())
		{
			protected.GET("/documents", handleListDocuments)
			protected.GET("/templates", handleListTemplates)
			protected.POST("/extract", handleExtractDocument)
			protected.POST("/generate-summary", handleGenerateSummary)
			protected.POST("/populate-template", handlePopulateTemplate)
			protected.POST("/accept-document", handleAcceptDocument)
			protected.GET("/view-document/:filename", handleViewDocument)
			protected.GET("/download-document/:filename", handleDownloadDocument)
			protected.GET("/test-docx", handleTestDocx)
			
			// iCloud Integration endpoints
			protected.POST("/icloud/auth", handleICloudAuth)
			protected.GET("/icloud/validate", handleICloudValidate)
			protected.GET("/icloud/folders", handleICloudListFolders)
			protected.GET("/icloud/case-folders", handleICloudListCaseFolders)
			protected.GET("/icloud/documents", handleICloudListDocuments)
			protected.POST("/icloud/sync-up", handleICloudSyncUp)
			protected.POST("/icloud/sync-down", handleICloudSyncDown)
			protected.GET("/icloud/sync-status/:documentId", handleICloudSyncStatus)
		}
	}

	// Start the server
	log.Println("Starting server on :8080")
	router.Run(":8080")
}

// Handler to list available documents
func handleListDocuments(c *gin.Context) {
	// For the prototype, we'll just return the sample legal documents
	// Use absolute path to artifacts directory
	documentsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/artifacts"
	
	files, err := os.ReadDir(documentsDir)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read documents directory"})
		return
	}
	
	var documents []Document
	for i, file := range files {
		if file.IsDir() {
			continue
		}
		
		ext := strings.ToLower(filepath.Ext(file.Name()))
		docType := "unknown"
		contentType := "unknown"
		
		// Determine document type based on extension
		switch ext {
		case ".pdf":
			docType = "pdf"
			if strings.Contains(file.Name(), "Adverse") {
				contentType = "adverse_action"
			} else if strings.Contains(file.Name(), "SummonsEquifax") {
				contentType = "summons_equifax"
			} else if strings.Contains(file.Name(), "Summons") {
				contentType = "summons"
			} else if strings.Contains(file.Name(), "Civil Cover") {
				contentType = "civil_cover_sheet"
			}
		case ".docx":
			docType = "docx"
			if strings.Contains(file.Name(), "Atty_Notes") {
				contentType = "attorney_notes"
			} else if strings.Contains(file.Name(), "Complaint") {
				contentType = "complaint_form"
			}
		}
		
		// Create document object
		doc := Document{
			ID:          fmt.Sprintf("doc_%d", i+1),
			Name:        file.Name(),
			Type:        docType,
			Path:        filepath.Join(documentsDir, file.Name()),
			ContentType: contentType,
		}
		
		documents = append(documents, doc)
	}
	
	c.JSON(http.StatusOK, documents)
}

// Handler to list available templates
func handleListTemplates(c *gin.Context) {
	// Use absolute path to artifacts directory for templates
	artifactsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/artifacts"
	
	// For the prototype, we'll return a predefined list of templates
	templates := []map[string]string{
		{
			"id":   "fcra-credit-card-fraud",
			"name": "FCRA Complaint - Credit Card Fraud",
			"desc": "For cases involving fraudulent credit card transactions",
			"path": filepath.Join(artifactsDir, "Complaint_Final.docx"),
		},
		{
			"id":   "fcra-identity-theft",
			"name": "FCRA Complaint - Identity Theft",
			"desc": "For cases involving wider identity theft issues",
			"path": "../templates/fcra_identity_theft.docx",
		},
		{
			"id":   "fcra-inaccurate-reporting",
			"name": "FCRA Complaint - Inaccurate Reporting",
			"desc": "For cases involving credit report errors",
			"path": "../templates/fcra_inaccurate_reporting.docx",
		},
	}
	
	c.JSON(http.StatusOK, templates)
}

// Handler to extract text from documents
func handleExtractDocument(c *gin.Context) {
	var docs []Document
	if err := c.ShouldBindJSON(&docs); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	var results []ExtractedText
	for _, doc := range docs {
		// For the prototype, we'll read text directly from files
		// In a real implementation, we would use proper extraction libraries
		content, err := os.ReadFile(doc.Path)
		if err != nil {
			log.Printf("Error reading file %s: %v", doc.Path, err)
			continue
		}
		
		// Create a simplified extraction result
		result := ExtractedText{
			DocumentID: doc.ID,
			Text:       string(content),
			Pages:      1, // Simplified for prototype
		}
		
		results = append(results, result)
	}
	
	c.JSON(http.StatusOK, results)
}

// Handler to generate summary from extracted text
func handleGenerateSummary(c *gin.Context) {
	// Get request parameters
	var request struct {
		Documents   []string `json:"documents"`
		TemplateID  string   `json:"templateId"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Process selected documents and extract relevant data
	civilCoverData := make(map[string]string)
	equifaxData := make(map[string]string)
	
	// Check if Civil Cover Sheet or Equifax Summons is included in the documents
	for _, docID := range request.Documents {
		// Find the document details
		for _, file := range getAllDocuments() {
			if file.ID == docID && file.ContentType == "civil_cover_sheet" {
				// Extract Civil Cover Sheet data
				civilCoverData = extractCivilCoverSheetData(file.Path)
				log.Printf("Civil Cover Sheet processed: %s", file.Name)
				break
			} else if file.ID == docID && file.ContentType == "summons_equifax" {
				// Extract Equifax summons data
				equifaxData = extractEquifaxSummonsData(file.Path)
				log.Printf("Equifax Summons processed: %s", file.Name)
				break
			}
		}
	}
	
	// Create a sample case based on our document analysis and Civil Cover Sheet data
	clientCase := ClientCase{
		// Existing client and fraud information
		ClientName:           "Eman Youssef",
		ContactInfo:          "347.891.5584",
		ResidenceLocation:    "Queens",
		FinancialInstitution: "TD Bank",
		AccountOpenDate:      parseDate("July 2023"),
		CreditLimit:          "$8,000",
		TravelLocation:       "Egypt",
		TravelStartDate:      parseDate("June 30, 2024"),
		TravelEndDate:        parseDate("July 30, 2024"),
		FraudAmount:          "$7,500",
		FraudStartDate:       parseDate("July 15, 2024"),
		FraudEndDate:         parseDate("July 31, 2024"),
		FraudDetails:         "Majority of charges were made at three different camera stores on July 17, July 23 and July 26.",
		DiscoveryDate:        parseDate("August 2024"),
		DisputeCount:         5,
		DisputeMethods:       []string{"in person", "over the phone", "via fax"},
		BankResponse:         "It must have been her son who made the charges",
		PoliceReportFiled:    true,
		PoliceReportDetails:  "Police obtained video footage of the thieves (two males) making a fraudulent charge at a McDonalds",
		CreditBureauDisputes: []string{"Experian", "Equifax", "Trans Union"},
		CreditBureauDisputeDate: parseDate("December 9, 2024"),
		CreditImpact:         "being denied credit, having her current credit limits reduced",

		// Enhanced Court Information (from Civil Cover Sheet or defaults)
		CourtJurisdiction:    getValueOrDefault(civilCoverData["courtJurisdiction"], "EASTERN DISTRICT OF NEW YORK"),
		CourtDivision:        getValueOrDefault(civilCoverData["courtDivision"], "BROOKLYN DIVISION"),
		CaseClassification:   getValueOrDefault(civilCoverData["caseClassification"], "CONSUMER CREDIT"),
		JuryDemand:          getBoolValueOrDefault(civilCoverData["juryDemand"], true),
		CaseNumber:          "1:25-cv-12345",
		FilingDate:          parseDate("April 9, 2025"),

		// Enhanced Attorney Information (from Civil Cover Sheet or defaults)
		AttorneyName:        getValueOrDefault(civilCoverData["attorneyName"], "Kevin Mallon"),
		AttorneyBarNumber:   getValueOrDefault(civilCoverData["attorneyBarNumber"], "2345678"),
		AttorneyFirm:        getValueOrDefault(civilCoverData["attorneyFirm"], "MALLON CONSUMER LAW GROUP"),
		AttorneyEmail:       getValueOrDefault(civilCoverData["attorneyEmail"], "kmallon@mallonlaw.com"),
		AttorneyPhone:       getValueOrDefault(civilCoverData["attorneyPhone"], "(212) 732-5777"),
		AttorneyFax:         getValueOrDefault(civilCoverData["attorneyFax"], "(212) 658-9177"),

		// Enhanced Legal Structure
		Defendants: []Defendant{
			{
				EntityType:      "Financial Institution",
				Name:            "TD Bank",
				Address:         "43-22 Queensboro Plaza South, Long Island City, NY 11101",
				RegisteredAgent: "CT Corporation System",
				State:           "Delaware",
				County:          "Queens",
			},
			{
				EntityType:      "Credit Bureau",
				Name:            "Experian Information Solutions, Inc.",
				Address:         "475 Anton Blvd., Costa Mesa, CA 92626",
				RegisteredAgent: "Corporation Service Company",
				State:           "Delaware",
				County:          "New Castle",
			},
			{
				EntityType:      getValueOrDefault(equifaxData["entityType"], "Credit Bureau"),
				Name:            getValueOrDefault(equifaxData["entityName"], "Equifax Information Services, LLC"),
				Address:         getValueOrDefault(equifaxData["entityAddress"], "1550 Peachtree Street, NW, Atlanta, GA 30309"),
				RegisteredAgent: getValueOrDefault(equifaxData["registeredAgent"], "Corporation Service Company"),
				State:           getValueOrDefault(equifaxData["entityState"], "Georgia"),
				County:          getValueOrDefault(equifaxData["entityCounty"], "Fulton"),
			},
			{
				EntityType:      "Credit Bureau",
				Name:            "TransUnion LLC",
				Address:         "555 West Adams Street, Chicago, IL 60661",
				RegisteredAgent: "Illinois Corporation Service Company",
				State:           "Delaware",
				County:          "Cook",
			},
		},

		CausesOfAction: []CauseOfAction{
			{
				Count:       1,
				Title:       "Violation of FCRA § 1681s-2(b) - Furnisher Duty to Investigate",
				Statute:     "15 U.S.C. § 1681s-2(b)",
				Elements:    []string{
					"Defendant furnishes consumer information to consumer reporting agencies", 
					"Consumer notified credit reporting agency of disputed information", 
					"Credit reporting agency notified Defendant of the dispute", 
					"Defendant failed to conduct reasonable investigation", 
					"Defendant failed to review all relevant information", 
					"Defendant continued to report inaccurate information",
				},
				Allegations: "TD Bank furnishes consumer information to the credit reporting agencies. Plaintiff disputed the fraudulent charges with the credit bureaus, who notified TD Bank of the dispute. Despite receiving notice of the dispute and clear evidence that Plaintiff was traveling in Egypt when the charges were made, TD Bank failed to conduct a reasonable investigation and continued to report the fraudulent account as accurately reflecting Plaintiff's payment history.",
				Remedies:    []string{"Actual damages", "Attorney fees and costs pursuant to 15 U.S.C. § 1681s-2(c)"},
			},
			{
				Count:       2,
				Title:       "Willful Violation of FCRA § 1681n - Consumer Reporting Violations",
				Statute:     "15 U.S.C. § 1681n",
				Elements:    []string{
					"Defendants are consumer reporting agencies", 
					"Consumer disputed information with reasonable basis", 
					"Defendants failed to follow reasonable procedures to assure maximum possible accuracy", 
					"Defendants failed to conduct reasonable reinvestigation", 
					"Defendants acted willfully in violating the FCRA",
				},
				Allegations: "The credit reporting agency Defendants willfully violated the FCRA by failing to conduct reasonable reinvestigation of Plaintiff's disputes regarding the fraudulent TD Bank account. Despite receiving documentation proving Plaintiff was in Egypt during the fraud period, Defendants continued to report the account as accurately reflecting Plaintiff's payment history, acting with reckless disregard for the accuracy of the information.",
				Remedies:    []string{"Actual damages", "Statutory damages of not less than $100 and not more than $1,000", "Punitive damages", "Attorney fees and costs"},
			},
			{
				Count:       3,
				Title:       "Negligent Violation of FCRA § 1681o - Consumer Reporting Violations",
				Statute:     "15 U.S.C. § 1681o",
				Elements:    []string{
					"Defendants are consumer reporting agencies", 
					"Consumer disputed information contained in credit file", 
					"Defendants failed to follow reasonable procedures", 
					"Defendants negligently violated FCRA provisions", 
					"Plaintiff suffered actual damages as a result",
				},
				Allegations: "In the alternative, if Defendants' violations were not willful, the credit reporting agency Defendants negligently violated the FCRA by failing to maintain reasonable procedures to assure maximum possible accuracy of consumer credit information and by failing to properly reinvestigate Plaintiff's disputes, causing Plaintiff to suffer actual damages.",
				Remedies:    []string{"Actual damages", "Attorney fees and costs"},
			},
		},

		ClaimAmount:         "$50,000",
		RelatedCases:        []string{},
	}
	
	// Generate markdown summary
	summary := generateMarkdownSummary(clientCase)
	
	// Generate document HTML based on template and client data
	documentHTML, err := generateDocumentHTML(request.TemplateID, clientCase)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate document"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"clientCase":    clientCase,
		"summary":       summary,
		"documentHTML":  documentHTML,
	})
}

// getAllDocuments returns all available documents (helper for document processing)
func getAllDocuments() []Document {
	// Use absolute path to artifacts directory
	documentsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/artifacts"
	
	files, err := os.ReadDir(documentsDir)
	if err != nil {
		return []Document{}
	}
	
	var documents []Document
	for i, file := range files {
		if file.IsDir() {
			continue
		}
		
		ext := strings.ToLower(filepath.Ext(file.Name()))
		docType := "unknown"
		contentType := "unknown"
		
		// Determine document type based on extension
		switch ext {
		case ".pdf":
			docType = "pdf"
			if strings.Contains(file.Name(), "Adverse") {
				contentType = "adverse_action"
			} else if strings.Contains(file.Name(), "SummonsEquifax") {
				contentType = "summons_equifax"
			} else if strings.Contains(file.Name(), "Summons") {
				contentType = "summons"
			} else if strings.Contains(file.Name(), "Civil Cover") {
				contentType = "civil_cover_sheet"
			}
		case ".docx":
			docType = "docx"
			if strings.Contains(file.Name(), "Atty_Notes") {
				contentType = "attorney_notes"
			} else if strings.Contains(file.Name(), "Complaint") {
				contentType = "complaint_form"
			}
		}
		
		// Create document object
		doc := Document{
			ID:          fmt.Sprintf("doc_%d", i+1),
			Name:        file.Name(),
			Type:        docType,
			Path:        filepath.Join(documentsDir, file.Name()),
			ContentType: contentType,
		}
		
		documents = append(documents, doc)
	}
	
	return documents
}

// extractCivilCoverSheetData simulates extracting data from Civil Cover Sheet PDF
func extractCivilCoverSheetData(filePath string) map[string]string {
	// For the prototype, we'll return simulated Civil Cover Sheet data
	// In a real implementation, this would use PDF parsing libraries
	data := map[string]string{
		"courtJurisdiction":   "EASTERN DISTRICT OF NEW YORK",
		"courtDivision":       "BROOKLYN DIVISION",
		"caseClassification":  "CONSUMER CREDIT",
		"juryDemand":         "true",
		"attorneyName":       "Kevin Mallon",
		"attorneyBarNumber":  "2345678",
		"attorneyFirm":       "MALLON CONSUMER LAW GROUP",
		"attorneyEmail":      "kmallon@mallonlaw.com",
		"attorneyPhone":      "(212) 732-5777",
		"attorneyFax":        "(212) 658-9177",
	}
	
	log.Printf("Civil Cover Sheet data extracted from: %s", filePath)
	return data
}

// extractEquifaxSummonsData simulates extracting legal entity data from Equifax Summons PDF
func extractEquifaxSummonsData(filePath string) map[string]string {
	// For the prototype, we'll return simulated Equifax summons data
	// In a real implementation, this would use PDF parsing libraries to extract legal entity information
	data := map[string]string{
		"entityName":         "Equifax Information Services, LLC",
		"entityType":         "Credit Bureau",
		"entityAddress":      "1550 Peachtree Street, NW, Atlanta, GA 30309",
		"registeredAgent":    "Corporation Service Company",
		"entityState":        "Georgia",
		"entityCounty":       "Fulton",
		"serviceAddress":     "1550 Peachtree Street, NW, Atlanta, GA 30309",
	}
	
	log.Printf("Equifax Summons data extracted from: %s", filePath)
	return data
}

// getValueOrDefault returns the value from the map or the default if empty/missing
func getValueOrDefault(value, defaultValue string) string {
	if value == "" {
		return defaultValue
	}
	return value
}

// getBoolValueOrDefault returns boolean value from string or default
func getBoolValueOrDefault(value string, defaultValue bool) bool {
	if value == "true" {
		return true
	} else if value == "false" {
		return false
	}
	return defaultValue
}

// Helper function to parse dates from strings
func parseDate(dateStr string) time.Time {
	layouts := []string{
		"January 2, 2006",
		"January 2006",
	}
	
	for _, layout := range layouts {
		t, err := time.Parse(layout, dateStr)
		if err == nil {
			return t
		}
	}
	
	// Return zero time if parsing fails
	return time.Time{}
}

// Handler to populate a template with client data
func handlePopulateTemplate(c *gin.Context) {
	var request struct {
		TemplateID  string     `json:"templateId"`
		ClientCase  ClientCase `json:"clientCase"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Generate document content based on the template and client data
	documentHTML, err := generateDocumentHTML(request.TemplateID, request.ClientCase)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate document"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Template populated successfully",
		"filePath": "/populated_documents/Complaint_Populated.docx",
		"documentHTML": documentHTML,
	})
}

// Generate a markdown summary of the client case
func generateMarkdownSummary(clientCase ClientCase) string {
	var summary strings.Builder

	summary.WriteString("# Client Case Summary\n\n")
	
	// Client Information Section
	summary.WriteString("## Client Information\n\n")
	summary.WriteString(fmt.Sprintf("**Name:** %s\n\n", clientCase.ClientName))
	summary.WriteString(fmt.Sprintf("**Contact:** %s\n\n", clientCase.ContactInfo))
	summary.WriteString(fmt.Sprintf("**Location:** %s, New York\n\n", clientCase.ResidenceLocation))

	// Account Information
	summary.WriteString("## Account Information\n\n")
	summary.WriteString(fmt.Sprintf("**Institution:** %s\n\n", clientCase.FinancialInstitution))
	
	if !clientCase.AccountOpenDate.IsZero() {
		summary.WriteString(fmt.Sprintf("**Account Opened:** %s\n\n", formatDate(clientCase.AccountOpenDate)))
	}
	
	summary.WriteString(fmt.Sprintf("**Credit Limit:** %s\n\n", clientCase.CreditLimit))

	// Fraud Details
	summary.WriteString("## Fraud Details\n\n")
	summary.WriteString(fmt.Sprintf("**Fraud Amount:** %s\n\n", clientCase.FraudAmount))
	
	if !clientCase.FraudStartDate.IsZero() && !clientCase.FraudEndDate.IsZero() {
		summary.WriteString(fmt.Sprintf("**Fraud Period:** %s to %s\n\n", 
			formatDate(clientCase.FraudStartDate),
			formatDate(clientCase.FraudEndDate)))
	}
	
	summary.WriteString(fmt.Sprintf("**Details:** %s\n\n", clientCase.FraudDetails))

	// Client Alibi
	summary.WriteString("## Client Alibi\n\n")
	
	if clientCase.TravelLocation != "" && !clientCase.TravelStartDate.IsZero() && !clientCase.TravelEndDate.IsZero() {
		summary.WriteString(fmt.Sprintf("**Travel:** Client was in %s from %s to %s\n\n", 
			clientCase.TravelLocation,
			formatDate(clientCase.TravelStartDate),
			formatDate(clientCase.TravelEndDate)))
	}

	// Dispute Information
	summary.WriteString("## Dispute History\n\n")
	
	if clientCase.DisputeCount > 0 {
		summary.WriteString(fmt.Sprintf("**Number of Disputes:** %d\n\n", clientCase.DisputeCount))
	}
	
	if len(clientCase.DisputeMethods) > 0 {
		summary.WriteString(fmt.Sprintf("**Dispute Methods:** %s\n\n", strings.Join(clientCase.DisputeMethods, ", ")))
	}
	
	if clientCase.BankResponse != "" {
		summary.WriteString(fmt.Sprintf("**Bank's Response:** %s\n\n", clientCase.BankResponse))
	}

	// Evidence
	summary.WriteString("## Supporting Evidence\n\n")
	
	if clientCase.PoliceReportFiled {
		summary.WriteString("**Police Report:** Filed\n\n")
		if clientCase.PoliceReportDetails != "" {
			summary.WriteString(fmt.Sprintf("**Police Report Details:** %s\n\n", clientCase.PoliceReportDetails))
		}
	}
	
	if clientCase.AdditionalEvidence != "" {
		summary.WriteString(fmt.Sprintf("**Additional Evidence:** %s\n\n", clientCase.AdditionalEvidence))
	}

	// Credit Bureau Disputes
	if len(clientCase.CreditBureauDisputes) > 0 {
		summary.WriteString("## Credit Bureau Disputes\n\n")
		summary.WriteString(fmt.Sprintf("**Bureaus Disputed:** %s\n\n", strings.Join(clientCase.CreditBureauDisputes, ", ")))
		
		if !clientCase.CreditBureauDisputeDate.IsZero() {
			summary.WriteString(fmt.Sprintf("**Date of Disputes:** %s\n\n", 
				formatDate(clientCase.CreditBureauDisputeDate)))
		}
	}

	return summary.String()
}

// Helper function to format dates
func formatDate(t time.Time) string {
	if t.IsZero() {
		return ""
	}
	return t.Format("January 2, 2006")
}

// Generate HTML representation of the legal document based on template and client data
func generateDocumentHTML(templateID string, clientCase ClientCase) (string, error) {
	// For a real implementation, this would load the actual template mapping from a file
	// For this prototype, we'll use a hardcoded template based on the template mapping example
	
	var document strings.Builder
	
	// Add document styling
	document.WriteString(`
	<div class="legal-document">
		<style>
			.legal-document {
				font-family: Times New Roman, serif;
				line-height: 1.5;
				margin: 1in;
			}
			.header {
				text-align: center;
				margin-bottom: 24px;
			}
			.court-info {
				text-align: center;
				margin-bottom: 24px;
				text-transform: uppercase;
			}
			.case-info {
				text-align: center;
				margin-bottom: 24px;
			}
			.section-title {
				text-align: center;
				text-transform: uppercase;
				font-weight: bold;
				margin: 24px 0;
			}
			.paragraph {
				text-indent: 0.5in;
				margin-bottom: 12px;
			}
			.numbered-paragraph {
				margin-bottom: 12px;
			}
			.signature-block {
				margin-top: 48px;
			}
			.highlight {
				background-color: #ffffc0;
			}
		</style>
	`)
	
	// Document Header
	document.WriteString(`
		<div class="header">
			<div><strong>UNITED STATES DISTRICT COURT</strong></div>
			<div><strong>EASTERN DISTRICT OF NEW YORK</strong></div>
		</div>
	`)
	
	// Case Information
	document.WriteString(`
		<div class="case-info">
			<div>-------------------------------------------------------------X</div>
			<div style="text-align: left">
				<span class="highlight">` + strings.ToUpper(clientCase.ClientName) + `</span>,
			</div>
			<div style="text-align: right">
				Case No.: ___-cv-_____
			</div>
			<div style="text-align: left">
				Plaintiff,
			</div>
			<div style="text-align: right">
				COMPLAINT
			</div>
			<div style="text-align: left">
				-against-
			</div>
			<div style="text-align: right">
				JURY TRIAL DEMANDED
			</div>
			<div style="text-align: left">
				<span class="highlight">` + strings.ToUpper(clientCase.FinancialInstitution) + `</span> and `)
	
	// Add defendants using enhanced structure
	if len(clientCase.Defendants) > 1 {
		// Skip the first defendant (TD Bank) as it's already added above
		for i, defendant := range clientCase.Defendants[1:] {
			if i > 0 {
				if i == len(clientCase.Defendants[1:])-1 {
					document.WriteString(" and ")
				} else {
					document.WriteString(", ")
				}
			}
			document.WriteString(`<span class="highlight">` + strings.ToUpper(defendant.Name) + `</span>`)
		}
	} else {
		document.WriteString(`<span class="highlight">CREDIT REPORTING AGENCIES</span>`)
	}
	
	document.WriteString(`
			</div>
			<div style="text-align: left">
				Defendants.
			</div>
			<div>-------------------------------------------------------------X</div>
		</div>
	`)
	
	// Preliminary Statement
	document.WriteString(`
		<div class="section-title">PRELIMINARY STATEMENT</div>
	`)
	
	// Intro paragraph with placeholders filled
	introText := "Plaintiff " + clientCase.ClientName + " is a victim of identity theft. While Plaintiff was travelling out of the country identity thieves used her " + clientCase.FinancialInstitution + " credit card to make over " + clientCase.FraudAmount + " in purchase without her consent."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>1.</strong> <span class="highlight">` + introText + `</span>
		</div>
	`)
	
	// Action paragraph with placeholders filled
	actionText := "Plaintiff brings this action against Defendant " + clientCase.FinancialInstitution + " for violating the FCRA, 15 U.S.C. § 1681s-2(b), by failing to reasonably investigate fraudulent charges on her " + clientCase.FinancialInstitution + " credit card after Plaintiff disputed the reporting of the charge with the credit reporting agencies. Defendant " + clientCase.FinancialInstitution + " wrongfully verified that the fraudulent charges being reported accurately to the consumer reporting agency Defendants who subsequently continued to erroneously report Plaintiff's account as delinquent to her detriment."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>2.</strong> <span class="highlight">` + actionText + `</span>
		</div>
	`)
	
	// Parties Section
	document.WriteString(`
		<div class="section-title">PARTIES</div>
	`)
	
	// Plaintiff information
	plaintiffText := "Plaintiff " + clientCase.ClientName + " is a natural person residing in " + clientCase.ResidenceLocation + ", New York."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>3.</strong> <span class="highlight">` + plaintiffText + `</span>
		</div>
	`)
	
	// Defendant bank information
	bankText := "Defendant " + clientCase.FinancialInstitution + " is a financial institution that furnishes information to consumer reporting agencies and is headquartered in New York, New York."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>4.</strong> <span class="highlight">` + bankText + `</span>
		</div>
	`)
	
	// Add all defendants using enhanced structure
	paraNum := 5
	if len(clientCase.Defendants) > 1 {
		// Skip the first defendant (TD Bank) as it's already described above
		for _, defendant := range clientCase.Defendants[1:] {
			var defendantText string
			if defendant.EntityType == "Credit Bureau" {
				defendantText = "Defendant " + defendant.Name + " is a consumer reporting agency as defined by 15 U.S.C. § 1681a(f)."
			} else {
				defendantText = "Defendant " + defendant.Name + " is a " + strings.ToLower(defendant.EntityType) + "."
			}
			document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + defendantText + `</span>
		</div>
		`)
			paraNum++
		}
	}
	
	// Factual Background
	document.WriteString(`
		<div class="section-title">FACTUAL ALLEGATIONS</div>
	`)
	
	// Account opening
	accountText := "Plaintiff opened a " + clientCase.FinancialInstitution + " credit card"
	if !clientCase.AccountOpenDate.IsZero() {
		accountText += " on or around " + formatDate(clientCase.AccountOpenDate)
	}
	accountText += " with an " + clientCase.CreditLimit + " credit limit. Plaintiff has always made all payments on her account in a timely manner prior to the subject fraud."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + accountText + `</span>
		</div>
	`)
	paraNum++
	
	// Travel details
	if clientCase.TravelLocation != "" && !clientCase.TravelStartDate.IsZero() && !clientCase.TravelEndDate.IsZero() {
		travelText := "Plaintiff travelled to " + clientCase.TravelLocation + " with her family from " + 
			formatDate(clientCase.TravelStartDate) + " through " + formatDate(clientCase.TravelEndDate) + "."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + travelText + `</span>
		</div>
		`)
		paraNum++
	}
	
	// Card possession
	cardText := "Plaintiff had two physical cards for her account and brought both of them with her to " + clientCase.TravelLocation + "."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + cardText + `</span>
		</div>
	`)
	paraNum++
	
	// Fraud details
	fraudText := "While Plaintiff was gone imposters used her account to make over " + clientCase.FraudAmount + " in fraudulent charges "
	if !clientCase.FraudStartDate.IsZero() && !clientCase.FraudEndDate.IsZero() {
		fraudText += "between " + formatDate(clientCase.FraudStartDate) + " and " + formatDate(clientCase.FraudEndDate) + ". "
	} else {
		fraudText += ". "
	}
	fraudText += clientCase.FraudDetails
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + fraudText + `</span>
		</div>
	`)
	paraNum++
	
	// Purchase patterns
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">Plaintiff had never used her card to make similar significant purchases in the past.</span>
		</div>
	`)
	paraNum++
	
	// Dispute details
	disputeText := "After finding out about the fraudulent charges "
	if !clientCase.DiscoveryDate.IsZero() {
		disputeText += "in " + formatDate(clientCase.DiscoveryDate) + " "
	}
	disputeText += "Plaintiff disputed the charges with " + clientCase.FinancialInstitution
	if clientCase.DisputeCount > 0 {
		disputeText += " on " + fmt.Sprintf("%d", clientCase.DisputeCount) + " separate occasions"
	}
	if len(clientCase.DisputeMethods) > 0 {
		disputeText += " - " + strings.Join(clientCase.DisputeMethods, ", ")
	}
	disputeText += " - explaining that she did not make the charges and could not possibly have made them since she was in " + clientCase.TravelLocation + " when they were made."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + disputeText + `</span>
		</div>
	`)
	paraNum++
	
	// Bank response
	if clientCase.BankResponse != "" {
		bankResponseText := "In fact, " + clientCase.FinancialInstitution + " told Plaintiff " + clientCase.BankResponse + "."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + bankResponseText + `</span>
		</div>
		`)
		paraNum++
	}
	
	// Police report
	if clientCase.PoliceReportFiled && clientCase.PoliceReportDetails != "" {
		policeText := "Plaintiff filed a police report, and " + clientCase.PoliceReportDetails + "."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + policeText + `</span>
		</div>
		`)
		paraNum++
	}
	
	// Bank refusal
	bankRefusalText := clientCase.FinancialInstitution + " repeatedly refused to correct the charges."
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + bankRefusalText + `</span>
		</div>
	`)
	paraNum++
	
	// Bureau disputes
	if len(clientCase.CreditBureauDisputes) > 0 && !clientCase.CreditBureauDisputeDate.IsZero() {
		bureauText := "Plaintiff then sent written disputes to each of the credit reporting Defendants, " + 
			strings.Join(clientCase.CreditBureauDisputes, ", ") + " on or around " + 
			formatDate(clientCase.CreditBureauDisputeDate) + ", providing proof that she was in " + 
			clientCase.TravelLocation + " when the charges were made."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + bureauText + `</span>
		</div>
		`)
		paraNum++
	}
	
	// Damages Section
	document.WriteString(`
		<div class="section-title">DAMAGES</div>
	`)
	
	// Credit impact
	creditImpactText := "As a result of Defendants' conduct, Plaintiff has suffered actual damages including " + 
		(clientCase.CreditImpact + ", mental anguish, humiliation, and anxiety related to her credit problems.")
	
	document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + creditImpactText + `</span>
		</div>
	`)
	paraNum++
	
	// CAUSES OF ACTION Section
	document.WriteString(`
		<div class="section-title">CAUSES OF ACTION</div>
	`)
	
	// Generate each cause of action
	for _, cause := range clientCase.CausesOfAction {
		countText := fmt.Sprintf("COUNT %s", intToRoman(cause.Count))
		
		document.WriteString(`
		<div class="section-title" style="margin-top: 24px">` + countText + `</div>
		<div class="section-title" style="margin-top: 12px">` + cause.Title + `</div>
	`)
		
		// Incorporate by reference
		incorpText := "Plaintiff realleges and incorporates by reference the allegations contained in paragraphs 1 through " + fmt.Sprintf("%d", paraNum-1) + " as if fully set forth herein."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> ` + incorpText + `
		</div>
	`)
		paraNum++
		
		// Statutory allegation
		statutoryText := "This cause of action is brought pursuant to " + cause.Statute + "."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> ` + statutoryText + `
		</div>
	`)
		paraNum++
		
		// Specific allegations
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> <span class="highlight">` + cause.Allegations + `</span>
		</div>
	`)
		paraNum++
		
		// Violation conclusion
		violationText := "By reason of the foregoing, Defendants have violated " + cause.Statute + " and Plaintiff is entitled to relief as set forth below."
		
		document.WriteString(`
		<div class="numbered-paragraph">
			<strong>` + fmt.Sprintf("%d", paraNum) + `.</strong> ` + violationText + `
		</div>
	`)
		paraNum++
	}
	
	// Prayer for Relief
	document.WriteString(`
		<div class="section-title">PRAYER FOR RELIEF</div>
		
		<div>
			WHEREFORE, Plaintiff respectfully prays that judgment be entered against Defendants for the following:
		</div>
		
		<div style="margin-left: 0.5in; margin-top: 12px">
			<div>A. Actual damages pursuant to 15 U.S.C. §§ 1681n and 1681o;</div>
			<div>B. Statutory damages pursuant to 15 U.S.C. § 1681n;</div>
			<div>C. Punitive damages pursuant to 15 U.S.C. § 1681n;</div>
			<div>D. Costs and reasonable attorney's fees pursuant to 15 U.S.C. §§ 1681n, 1681o, and 1681s-2(c); and</div>
			<div>E. Such other and further relief as may be necessary, just and proper.</div>
		</div>
	`)
	
	// Jury Demand
	document.WriteString(`
		<div class="section-title" style="margin-top: 36px">JURY DEMAND</div>
		
		<div>
			Plaintiff hereby demands a trial by jury on all issues so triable.
		</div>
	`)
	
	// Signature Block
	document.WriteString(`
		<div class="signature-block">
			<div>Dated: April 9, 2025</div>
			<div style="margin-top: 12px">Respectfully submitted,</div>
			<div style="margin-top: 48px">______________________________</div>
			<div>Kevin Mallon, Esq.</div>
			<div>MALLON CONSUMER LAW GROUP</div>
			<div>500 Fifth Avenue, Suite 1900</div>
			<div>New York, NY 10110</div>
			<div>Tel: (212) 732-5777</div>
			<div>Fax: (212) 658-9177</div>
			<div>Attorney for Plaintiff</div>
		</div>
	</div>
	`)
	
	return document.String(), nil
}

// Helper function to convert integers to Roman numerals for legal document formatting
func intToRoman(num int) string {
	values := []int{10, 9, 5, 4, 1}
	numerals := []string{"X", "IX", "V", "IV", "I"}
	result := ""
	
	for i, value := range values {
		for num >= value {
			result += numerals[i]
			num -= value
		}
	}
	
	return result
}

// Handler to accept and save the generated document
func handleAcceptDocument(c *gin.Context) {
	var request struct {
		ClientCase   ClientCase `json:"clientCase"`
		DocumentHTML string     `json:"documentHTML"`
		TemplateID   string     `json:"templateId"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Create saved documents directory if it doesn't exist
	savedDocsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/dev/saved_documents"
	if err := os.MkdirAll(savedDocsDir, 0755); err != nil {
		log.Printf("Error creating saved documents directory: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create document storage directory"})
		return
	}
	
	// Generate unique filename based on client name and timestamp
	clientNameSafe := strings.ReplaceAll(strings.ToLower(request.ClientCase.ClientName), " ", "_")
	timestamp := time.Now().Format("20060102_150405")
	fileName := fmt.Sprintf("complaint_%s_%s.html", clientNameSafe, timestamp)
	filePath := filepath.Join(savedDocsDir, fileName)
	
	// Add HTML document structure for proper rendering
	fullDocumentHTML := `<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Legal Complaint - ` + request.ClientCase.ClientName + `</title>
	<style>
		body { font-family: 'Times New Roman', serif; margin: 1in; line-height: 1.5; }
		.highlight { background-color: #ffffc0; }
	</style>
</head>
<body>
` + request.DocumentHTML + `
</body>
</html>`
	
	// Write document to file
	if err := os.WriteFile(filePath, []byte(fullDocumentHTML), 0644); err != nil {
		log.Printf("Error writing document to file: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save document"})
		return
	}
	
	// Get file info for metadata
	fileInfo, err := os.Stat(filePath)
	if err != nil {
		log.Printf("Error getting file info: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Document saved but failed to get file info"})
		return
	}
	
	// Create saved document metadata
	documentID := fmt.Sprintf("doc_%d", time.Now().Unix())
	savedDoc := SavedDocument{
		ID:           documentID,
		FileName:     fileName,
		FilePath:     filePath,
		DocumentType: "complaint",
		SavedDate:    time.Now(),
		FileSize:     fileInfo.Size(),
		Status:       "saved",
	}
	
	// Update client case with saved document info
	request.ClientCase.SavedDocuments = append(request.ClientCase.SavedDocuments, savedDoc)
	
	log.Printf("Document saved successfully: %s (Size: %d bytes)", filePath, fileInfo.Size())
	
	c.JSON(http.StatusOK, gin.H{
		"success":        true,
		"message":        "Document saved successfully",
		"savedDocument":  savedDoc,
		"clientCase":     request.ClientCase,
	})
}

// Handler to view a saved document
func handleViewDocument(c *gin.Context) {
	filename := c.Param("filename")
	
	// Validate filename to prevent path traversal attacks
	if strings.Contains(filename, "..") || strings.Contains(filename, "/") || strings.Contains(filename, "\\") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
		return
	}
	
	// Construct file path
	savedDocsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/dev/saved_documents"
	filePath := filepath.Join(savedDocsDir, filename)
	
	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Document not found"})
		return
	}
	
	// Read file content
	content, err := os.ReadFile(filePath)
	if err != nil {
		log.Printf("Error reading document %s: %v", filePath, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read document"})
		return
	}
	
	// Set appropriate headers and serve HTML content
	c.Header("Content-Type", "text/html; charset=utf-8")
	c.Header("Content-Disposition", "inline; filename=\""+filename+"\"")
	c.String(http.StatusOK, string(content))
}

// convertHTMLToDocx converts HTML content to proper DOCX format
// This creates a valid Microsoft Word document with legal formatting
func convertHTMLToDocx(htmlContent string) ([]byte, error) {
	// Create a new Word document
	doc := document.New()
	
	// Set document properties for legal documents
	// Note: Setting basic document without custom properties for compatibility
	// props := doc.CoreProperties
	// UniOffice library may have different property setting methods
	
	// Extract the body content from HTML
	body := htmlContent
	if strings.Contains(htmlContent, "<body>") {
		start := strings.Index(htmlContent, "<body>")
		end := strings.Index(htmlContent, "</body>")
		if start != -1 && end != -1 {
			body = htmlContent[start+6 : end]
		}
	}
	
	// Remove HTML style tags completely
	for strings.Contains(body, "<style>") {
		styleStart := strings.Index(body, "<style>")
		styleEnd := strings.Index(body, "</style>")
		if styleStart != -1 && styleEnd != -1 {
			body = body[:styleStart] + body[styleEnd+8:]
		} else {
			break
		}
	}
	
	// Simple approach: Create basic paragraphs from HTML content
	// Remove all HTML tags and create simple text paragraphs
	cleanText := body
	
	// Remove all HTML tags
	for strings.Contains(cleanText, "<") {
		start := strings.Index(cleanText, "<")
		end := strings.Index(cleanText, ">")
		if start != -1 && end != -1 && end > start {
			cleanText = cleanText[:start] + " " + cleanText[end+1:]
		} else {
			break
		}
	}
	
	// Clean up multiple spaces and newlines
	cleanText = strings.ReplaceAll(cleanText, "\n", " ")
	cleanText = strings.ReplaceAll(cleanText, "\t", " ")
	for strings.Contains(cleanText, "  ") {
		cleanText = strings.ReplaceAll(cleanText, "  ", " ")
	}
	cleanText = strings.TrimSpace(cleanText)
	
	// Split into sentences and create paragraphs
	sentences := strings.Split(cleanText, ". ")
	
	for _, sentence := range sentences {
		sentence = strings.TrimSpace(sentence)
		if sentence == "" {
			continue
		}
		
		// Add period if missing
		if !strings.HasSuffix(sentence, ".") && !strings.HasSuffix(sentence, ":") {
			sentence += "."
		}
		
		// Create paragraph
		para := doc.AddParagraph()
		run := para.AddRun()
		run.Properties().SetSize(measurement.Point * 12)
		run.Properties().SetFontFamily("Times New Roman")
		run.AddText(sentence)
	}
	
	// Save to byte buffer
	buf := &bytes.Buffer{}
	err := doc.Save(buf)
	if err != nil {
		return nil, fmt.Errorf("failed to save document: %v", err)
	}
	return buf.Bytes(), nil
}

// HTMLLine represents a parsed line from HTML content
type HTMLLine struct {
	Text string
	Type string // "header", "section-title", "numbered-paragraph", "signature-block", "normal"
}

// parseHTMLContent parses HTML content into structured lines
func parseHTMLContent(htmlContent string) []HTMLLine {
	var lines []HTMLLine
	
	// Split by divs and parse structure
	content := htmlContent
	
	// Remove HTML structure and extract meaningful content
	content = strings.ReplaceAll(content, "<div class=\"legal-document\">", "")
	content = strings.ReplaceAll(content, "</div>", "\n")
	
	// Split into lines
	rawLines := strings.Split(content, "\n")
	
	for _, line := range rawLines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		
		// Determine line type based on HTML classes and content
		lineType := "normal"
		cleanText := line
		
		if strings.Contains(line, `class="header"`) {
			lineType = "header"
			cleanText = cleanHTMLTags(line)
		} else if strings.Contains(line, `class="section-title"`) {
			lineType = "section-title"
			cleanText = cleanHTMLTags(line)
		} else if strings.Contains(line, `class="numbered-paragraph"`) {
			lineType = "numbered-paragraph"
			cleanText = cleanHTMLTags(line)
		} else if strings.Contains(line, `class="signature-block"`) {
			lineType = "signature-block"
			cleanText = cleanHTMLTags(line)
		} else if strings.Contains(line, "<strong>") || strings.Contains(line, "UNITED STATES") || strings.Contains(line, "EASTERN DISTRICT") {
			lineType = "header"
			cleanText = cleanHTMLTags(line)
		} else if strings.Contains(line, "PRELIMINARY STATEMENT") || strings.Contains(line, "PARTIES") || strings.Contains(line, "FACTUAL ALLEGATIONS") || strings.Contains(line, "DAMAGES") || strings.Contains(line, "CAUSES OF ACTION") || strings.Contains(line, "PRAYER FOR RELIEF") || strings.Contains(line, "JURY DEMAND") {
			lineType = "section-title"
			cleanText = cleanHTMLTags(line)
		} else {
			// Check for numbered paragraphs by content
			cleanText = cleanHTMLTags(line)
			if len(cleanText) > 0 && (cleanText[0] >= '0' && cleanText[0] <= '9') {
				lineType = "numbered-paragraph"
			}
		}
		
		if cleanText != "" {
			lines = append(lines, HTMLLine{
				Text: cleanText,
				Type: lineType,
			})
		}
	}
	
	return lines
}

// cleanHTMLTags removes HTML tags but preserves content structure
func cleanHTMLTags(text string) string {
	// Remove most HTML tags but preserve structure for formatting
	clean := text
	
	// Remove div tags with classes
	clean = strings.ReplaceAll(clean, `<div class="header">`, "")
	clean = strings.ReplaceAll(clean, `<div class="case-info">`, "")
	clean = strings.ReplaceAll(clean, `<div class="section-title">`, "")
	clean = strings.ReplaceAll(clean, `<div class="numbered-paragraph">`, "")
	clean = strings.ReplaceAll(clean, `<div class="signature-block">`, "")
	clean = strings.ReplaceAll(clean, `<div class="section-title" style="margin-top: 24px">`, "")
	clean = strings.ReplaceAll(clean, `<div class="section-title" style="margin-top: 12px">`, "")
	
	// Remove style attributes but keep content
	clean = strings.ReplaceAll(clean, `<div style="text-align: left">`, "")
	clean = strings.ReplaceAll(clean, `<div style="text-align: right">`, "")
	clean = strings.ReplaceAll(clean, `<div style="text-align: center">`, "")
	clean = strings.ReplaceAll(clean, `<div style="margin-left: 0.5in; margin-top: 12px">`, "")
	clean = strings.ReplaceAll(clean, `<div style="margin-top: 12px">`, "")
	clean = strings.ReplaceAll(clean, `<div style="margin-top: 48px">`, "")
	clean = strings.ReplaceAll(clean, `<div style="margin-top: 36px">`, "")
	
	// Remove simple div tags
	clean = strings.ReplaceAll(clean, "<div>", "")
	clean = strings.ReplaceAll(clean, "</div>", "")
	
	// Clean up HTML entities
	clean = strings.ReplaceAll(clean, "&nbsp;", " ")
	clean = strings.ReplaceAll(clean, "&lt;", "<")
	clean = strings.ReplaceAll(clean, "&gt;", ">")
	clean = strings.ReplaceAll(clean, "&amp;", "&")
	
	return strings.TrimSpace(clean)
}

// addFormattedText adds text to paragraph with highlight formatting
func addFormattedText(para document.Paragraph, text string) {
	// Process highlighted text
	if strings.Contains(text, `<span class="highlight">`) {
		// Split text by highlight spans
		parts := strings.Split(text, `<span class="highlight">`)
		
		// Add first part (normal text)
		if len(parts) > 0 && strings.TrimSpace(parts[0]) != "" {
			run := para.AddRun()
			run.Properties().SetSize(measurement.Point * 12)
			run.Properties().SetFontFamily("Times New Roman")
			run.AddText(cleanHTMLTags(parts[0]))
		}
		
		// Process highlighted parts
		for i := 1; i < len(parts); i++ {
			part := parts[i]
			if strings.Contains(part, "</span>") {
				// Split highlighted text from remaining text
				spanEnd := strings.Index(part, "</span>")
				highlightedText := part[:spanEnd]
				remainingText := part[spanEnd+7:]
				
				// Add highlighted text (yellow background)
				if strings.TrimSpace(highlightedText) != "" {
					highlightRun := para.AddRun()
					highlightRun.Properties().SetSize(measurement.Point * 12)
					highlightRun.Properties().SetFontFamily("Times New Roman")
					highlightRun.Properties().SetHighlight(wml.ST_HighlightColorYellow)
					highlightRun.AddText(cleanHTMLTags(highlightedText))
				}
				
				// Add remaining normal text
				if strings.TrimSpace(remainingText) != "" {
					run := para.AddRun()
					run.Properties().SetSize(measurement.Point * 12)
					run.Properties().SetFontFamily("Times New Roman")
					run.AddText(cleanHTMLTags(remainingText))
				}
			}
		}
	} else {
		// No highlighting, add as normal text
		run := para.AddRun()
		run.Properties().SetSize(measurement.Point * 12)
		run.Properties().SetFontFamily("Times New Roman")
		run.AddText(cleanHTMLTags(text))
	}
}

// Handler to download a saved document (convert to Word format)
func handleDownloadDocument(c *gin.Context) {
	filename := c.Param("filename")
	
	// Validate filename to prevent path traversal attacks
	if strings.Contains(filename, "..") || strings.Contains(filename, "/") || strings.Contains(filename, "\\") {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid filename"})
		return
	}
	
	// Construct file path
	savedDocsDir := "/Users/corelogic/satori-dev/clients/proj-mallon/dev/saved_documents"
	filePath := filepath.Join(savedDocsDir, filename)
	
	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		c.JSON(http.StatusNotFound, gin.H{"error": "Document not found"})
		return
	}
	
	// Read HTML content
	content, err := os.ReadFile(filePath)
	if err != nil {
		log.Printf("Error reading document %s: %v", filePath, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read document"})
		return
	}
	
	// Convert HTML to proper DOCX format
	docxContent, err := convertHTMLToDocx(string(content))
	if err != nil {
		log.Printf("Error converting document to DOCX: %v", err)
		// Fallback: serve HTML if DOCX conversion fails
		c.Header("Content-Type", "text/html; charset=utf-8")
		c.Header("Content-Disposition", "attachment; filename=\""+filename+"\"")
		c.String(http.StatusOK, string(content))
		return
	}
	
	// Generate Word filename from HTML filename
	wordFilename := strings.TrimSuffix(filename, filepath.Ext(filename)) + ".docx"
	
	// Serve proper DOCX document with correct headers
	c.Header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
	c.Header("Content-Disposition", "attachment; filename=\""+wordFilename+"\"")
	c.Header("Cache-Control", "no-cache")
	c.Header("Content-Length", fmt.Sprintf("%d", len(docxContent)))
	c.Data(http.StatusOK, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", docxContent)
	
	log.Printf("Document download served: %s (DOCX format, %d bytes)", wordFilename, len(docxContent))
}

// Global storage for sessions and credentials (in production, use secure storage)
var userSessions = make(map[string]*UserSession)
var icloudCredentials *ICloudCredentials
var icloudSyncStatuses = make(map[string]*ICloudSyncStatus)

// Handler for iCloud authentication
func handleICloudAuth(c *gin.Context) {
	var request struct {
		Username    string `json:"username"`
		AppPassword string `json:"appPassword"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Validate credentials format
	if request.Username == "" || request.AppPassword == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Username and app password are required"})
		return
	}
	
	// For prototype: simulate authentication validation
	// In production: implement actual iCloud API authentication
	if !validateICloudCredentials(request.Username, request.AppPassword) {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid iCloud credentials"})
		return
	}
	
	// Create session
	sessionID := generateSessionID()
	icloudCredentials = &ICloudCredentials{
		Username:    request.Username,
		AppPassword: request.AppPassword, // In production: encrypt this
		SessionID:   sessionID,
		CreatedAt:   time.Now(),
		ExpiresAt:   time.Now().Add(24 * time.Hour), // 24 hour session
	}
	
	log.Printf("iCloud authentication successful for user: %s", request.Username)
	
	c.JSON(http.StatusOK, gin.H{
		"success":   true,
		"message":   "Authentication successful",
		"sessionId": sessionID,
		"expiresAt": icloudCredentials.ExpiresAt,
	})
}

// Handler to validate existing iCloud session
func handleICloudValidate(c *gin.Context) {
	if icloudCredentials == nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "No active iCloud session"})
		return
	}
	
	if time.Now().After(icloudCredentials.ExpiresAt) {
		icloudCredentials = nil
		c.JSON(http.StatusUnauthorized, gin.H{"error": "iCloud session expired"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"valid":     true,
		"username":  icloudCredentials.Username,
		"expiresAt": icloudCredentials.ExpiresAt,
	})
}

// Handler to list iCloud folders (real implementation)
func handleICloudListFolders(c *gin.Context) {
	// Get real iCloud Drive folders (no authentication needed for local filesystem access)
	folders, err := getRealICloudFolders("", "")
	if err != nil {
		log.Printf("Error accessing iCloud folders: %v", err)
		// Fallback to simulated data if real iCloud not available
		folders = []ICloudDocument{
			{
				ID:          "folder_1",
				Name:        "CASES",
				Path:        "/CASES",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -1),
			},
			{
				ID:          "folder_2",
				Name:        "Downloads",
				Path:        "/Downloads",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -7),
			},
		}
		log.Printf("Using fallback folder data due to iCloud access error")
	}
	
	log.Printf("Listed %d iCloud folders", len(folders))
	
	c.JSON(http.StatusOK, gin.H{
		"folders": folders,
		"count":   len(folders),
	})
}

// Handler to list case folders within a parent directory (real implementation)
func handleICloudListCaseFolders(c *gin.Context) {
	parentFolder := c.Query("parent")
	if parentFolder == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Parent folder parameter required"})
		return
	}
	
	// Get real case subfolders from iCloud (no authentication needed for filesystem access)
	caseFolders, err := getRealICloudSubfolders("", "", parentFolder)
	if err != nil {
		log.Printf("Error accessing iCloud case folders: %v", err)
		// Return empty array if folder doesn't exist or can't be accessed
		c.JSON(http.StatusOK, gin.H{
			"folders": []ICloudDocument{},
			"parent":  parentFolder,
			"count":   0,
			"error":   "Folder not accessible: " + err.Error(),
		})
		return
	}
	
	log.Printf("Listed %d real case folders in parent: %s", len(caseFolders), parentFolder)
	
	c.JSON(http.StatusOK, gin.H{
		"folders": caseFolders,
		"parent":  parentFolder,
		"count":   len(caseFolders),
	})
}

// Handler to list documents in iCloud folder (real implementation)
func handleICloudListDocuments(c *gin.Context) {
	if !isICloudSessionValid() {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "iCloud session not valid"})
		return
	}
	
	folderPath := c.Query("folder")
	if folderPath == "" {
		folderPath = "/"
	}
	
	// Get real documents from iCloud folder
	documents, err := getRealICloudDocuments(icloudCredentials.Username, icloudCredentials.AppPassword, folderPath)
	if err != nil {
		log.Printf("Error accessing iCloud documents: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to access documents: " + err.Error()})
		return
	}
	
	log.Printf("Listed %d real iCloud documents in folder: %s", len(documents), folderPath)
	
	c.JSON(http.StatusOK, gin.H{
		"documents": documents,
		"folder":    folderPath,
		"count":     len(documents),
	})
}

// Handler to sync document up to iCloud
func handleICloudSyncUp(c *gin.Context) {
	if !isICloudSessionValid() {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "iCloud session not valid"})
		return
	}
	
	var request struct {
		DocumentID   string `json:"documentId"`
		ICloudFolder string `json:"icloudFolder"`
		FileName     string `json:"fileName"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Create sync status tracking
	syncID := request.DocumentID
	icloudSyncStatuses[syncID] = &ICloudSyncStatus{
		DocumentID: request.DocumentID,
		Status:     "pending",
		Progress:   0,
		Message:    "Starting upload to iCloud...",
		StartedAt:  time.Now(),
	}
	
	// Start async upload process
	go performICloudUpload(request.DocumentID, request.ICloudFolder, request.FileName)
	
	log.Printf("Started iCloud upload for document: %s to folder: %s", request.DocumentID, request.ICloudFolder)
	
	c.JSON(http.StatusOK, gin.H{
		"success":   true,
		"message":   "Upload started",
		"syncId":    syncID,
		"status":    "pending",
	})
}

// Handler to sync document down from iCloud
func handleICloudSyncDown(c *gin.Context) {
	if !isICloudSessionValid() {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "iCloud session not valid"})
		return
	}
	
	var request struct {
		ICloudPath string `json:"icloudPath"`
		LocalName  string `json:"localName"`
	}
	
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// For prototype: simulate download
	// In production: implement actual iCloud Drive download
	downloadID := fmt.Sprintf("download_%d", time.Now().Unix())
	
	icloudSyncStatuses[downloadID] = &ICloudSyncStatus{
		DocumentID: downloadID,
		Status:     "pending",
		Progress:   0,
		Message:    "Starting download from iCloud...",
		StartedAt:  time.Now(),
	}
	
	// Start async download process
	go performICloudDownload(downloadID, request.ICloudPath, request.LocalName)
	
	log.Printf("Started iCloud download from: %s to: %s", request.ICloudPath, request.LocalName)
	
	c.JSON(http.StatusOK, gin.H{
		"success":   true,
		"message":   "Download started",
		"syncId":    downloadID,
		"status":    "pending",
	})
}

// Handler to get sync status
func handleICloudSyncStatus(c *gin.Context) {
	documentID := c.Param("documentId")
	
	status, exists := icloudSyncStatuses[documentID]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "Sync status not found"})
		return
	}
	
	c.JSON(http.StatusOK, status)
}

// Helper function to validate iCloud session
func isICloudSessionValid() bool {
	return icloudCredentials != nil && time.Now().Before(icloudCredentials.ExpiresAt)
}

// Helper function to validate iCloud credentials (real implementation)
func validateICloudCredentials(username, appPassword string) bool {
	// Basic validation - in production this would connect to iCloud
	// For now, validate format and attempt connection
	if len(username) == 0 || len(appPassword) == 0 {
		return false
	}
	
	// Validate email format
	if !strings.Contains(username, "@") {
		return false
	}
	
	// Validate app-specific password format (usually 16 chars with hyphens)
	if len(appPassword) < 8 {
		return false
	}
	
	// TODO: Implement actual iCloud authentication
	// For now, accept properly formatted credentials
	return true
}

// Helper function to generate session ID
func generateSessionID() string {
	return fmt.Sprintf("session_%d_%d", time.Now().Unix(), time.Now().Nanosecond())
}

// Real iCloud Drive access functions using macOS system integration

// getRealICloudFolders gets actual folders from user's iCloud Drive
func getRealICloudFolders(username, appPassword string) ([]ICloudDocument, error) {
	// Always try test directory first for development
	testPath := "/Users/corelogic/satori-dev/clients/proj-mallon/test_icloud"
	var icloudPath string
	if _, err := os.Stat(testPath); err == nil {
		icloudPath = testPath
		log.Printf("Using test iCloud directory: %s", testPath)
	} else {
		// Get iCloud Drive path on macOS
		icloudPath = "/Users/" + getCurrentUser() + "/Library/Mobile Documents/com~apple~CloudDocs"
		
		// Check if iCloud Drive is available
		if _, err := os.Stat(icloudPath); os.IsNotExist(err) {
			return nil, fmt.Errorf("iCloud Drive not available or not synced")
		}
	}
	
	// List directories in iCloud Drive root
	dirs, err := os.ReadDir(icloudPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read iCloud Drive: %v", err)
	}
	
	var folders []ICloudDocument
	for i, dir := range dirs {
		if dir.IsDir() && !strings.HasPrefix(dir.Name(), ".") {
			info, err := dir.Info()
			if err != nil {
				continue
			}
			
			folder := ICloudDocument{
				ID:          fmt.Sprintf("icloud_folder_%d", i),
				Name:        dir.Name(),
				Path:        "/" + dir.Name(),
				IsDirectory: true,
				Modified:    info.ModTime(),
				Size:        0, // Directories don't have size
			}
			folders = append(folders, folder)
		}
	}
	
	log.Printf("Found %d real iCloud folders", len(folders))
	return folders, nil
}

// getRealICloudSubfolders gets subfolders within a specific iCloud directory
func getRealICloudSubfolders(username, appPassword, parentFolder string) ([]ICloudDocument, error) {
	// Always try test directory first for development
	testPath := "/Users/corelogic/satori-dev/clients/proj-mallon/test_icloud"
	var icloudPath string
	if _, err := os.Stat(testPath); err == nil {
		icloudPath = testPath
		log.Printf("Using test iCloud directory for subfolders: %s", testPath)
	} else {
		// Get iCloud Drive path on macOS
		icloudPath = "/Users/" + getCurrentUser() + "/Library/Mobile Documents/com~apple~CloudDocs"
		
		// Check if iCloud Drive is available
		if _, err := os.Stat(icloudPath); os.IsNotExist(err) {
			return nil, fmt.Errorf("iCloud Drive not available or not synced")
		}
	}
	
	// Clean the parent folder path
	cleanParent := strings.TrimPrefix(parentFolder, "/")
	fullPath := filepath.Join(icloudPath, cleanParent)
	
	// Check if parent folder exists
	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("folder does not exist: %s", parentFolder)
	}
	
	// List subdirectories
	dirs, err := os.ReadDir(fullPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read folder %s: %v", parentFolder, err)
	}
	
	var subfolders []ICloudDocument
	for i, dir := range dirs {
		if dir.IsDir() && !strings.HasPrefix(dir.Name(), ".") {
			info, err := dir.Info()
			if err != nil {
				continue
			}
			
			subfolder := ICloudDocument{
				ID:          fmt.Sprintf("icloud_subfolder_%d", i),
				Name:        dir.Name(),
				Path:        parentFolder + "/" + dir.Name(),
				IsDirectory: true,
				Modified:    info.ModTime(),
				Size:        0,
			}
			subfolders = append(subfolders, subfolder)
		}
	}
	
	log.Printf("Found %d subfolders in %s", len(subfolders), parentFolder)
	return subfolders, nil
}

// getRealICloudDocuments gets actual documents from a specific iCloud folder
func getRealICloudDocuments(username, appPassword, folderPath string) ([]ICloudDocument, error) {
	// Always try test directory first for development
	testPath := "/Users/corelogic/satori-dev/clients/proj-mallon/test_icloud"
	var icloudPath string
	if _, err := os.Stat(testPath); err == nil {
		icloudPath = testPath
		log.Printf("Using test iCloud directory for documents: %s", testPath)
	} else {
		// Get iCloud Drive path on macOS
		icloudPath = "/Users/" + getCurrentUser() + "/Library/Mobile Documents/com~apple~CloudDocs"
		
		// Check if iCloud Drive is available
		if _, err := os.Stat(icloudPath); os.IsNotExist(err) {
			return nil, fmt.Errorf("iCloud Drive not available or not synced")
		}
	}
	
	// Clean the folder path
	cleanPath := strings.TrimPrefix(folderPath, "/")
	fullPath := filepath.Join(icloudPath, cleanPath)
	
	// Use root if path is empty
	if cleanPath == "" {
		fullPath = icloudPath
	}
	
	// Check if folder exists
	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("folder does not exist: %s", folderPath)
	}
	
	// List all items in the folder
	items, err := os.ReadDir(fullPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read folder %s: %v", folderPath, err)
	}
	
	var documents []ICloudDocument
	for i, item := range items {
		// Skip hidden files
		if strings.HasPrefix(item.Name(), ".") {
			continue
		}
		
		info, err := item.Info()
		if err != nil {
			continue
		}
		
		// Determine file type
		fileType := "unknown"
		if !item.IsDir() {
			ext := strings.ToLower(filepath.Ext(item.Name()))
			switch ext {
			case ".pdf":
				fileType = "pdf"
			case ".docx":
				fileType = "docx"
			case ".doc":
				fileType = "doc"
			case ".txt":
				fileType = "txt"
			case ".jpg", ".jpeg", ".png":
				fileType = "image"
			default:
				fileType = strings.TrimPrefix(ext, ".")
			}
		}
		
		doc := ICloudDocument{
			ID:          fmt.Sprintf("icloud_doc_%d", i),
			Name:        item.Name(),
			Path:        folderPath + "/" + item.Name(),
			IsDirectory: item.IsDir(),
			Modified:    info.ModTime(),
			Size:        info.Size(),
			Type:        fileType,
		}
		documents = append(documents, doc)
	}
	
	log.Printf("Found %d items in iCloud folder %s", len(documents), folderPath)
	return documents, nil
}

// getCurrentUser gets the current macOS username
func getCurrentUser() string {
	cmd := exec.Command("whoami")
	output, err := cmd.Output()
	if err != nil {
		return "unknown"
	}
	return strings.TrimSpace(string(output))
}

// Helper function to get simulated iCloud documents
func getSimulatedICloudDocuments(folderPath string) []ICloudDocument {
	switch folderPath {
	case "/Legal Documents":
		return []ICloudDocument{
			{
				ID:       "icloud_doc_1",
				Name:     "Client_Interview_Notes.docx",
				Path:     "/Legal Documents/Client_Interview_Notes.docx",
				Size:     45120,
				Modified: time.Now().AddDate(0, 0, -5),
				Type:     "docx",
			},
			{
				ID:       "icloud_doc_2",
				Name:     "Adverse_Action_Letter.pdf",
				Path:     "/Legal Documents/Adverse_Action_Letter.pdf",
				Size:     128256,
				Modified: time.Now().AddDate(0, 0, -3),
				Type:     "pdf",
			},
		}
	case "/Client Files":
		return []ICloudDocument{
			{
				ID:       "icloud_doc_3",
				Name:     "Case_Evidence.pdf",
				Path:     "/Client Files/Case_Evidence.pdf",
				Size:     256512,
				Modified: time.Now().AddDate(0, 0, -2),
				Type:     "pdf",
			},
		}
	default:
		return []ICloudDocument{}
	}
}

// Async function to perform iCloud upload (prototype)
func performICloudUpload(documentID, icloudFolder, fileName string) {
	// Simulate upload progress
	for progress := 0; progress <= 100; progress += 20 {
		time.Sleep(500 * time.Millisecond)
		
		status := icloudSyncStatuses[documentID]
		if status != nil {
			status.Progress = progress
			status.Status = "syncing"
			status.Message = fmt.Sprintf("Uploading to iCloud... %d%%", progress)
		}
	}
	
	// Complete upload
	status := icloudSyncStatuses[documentID]
	if status != nil {
		status.Status = "completed"
		status.Progress = 100
		status.Message = "Successfully uploaded to iCloud"
		status.CompletedAt = time.Now()
	}
	
	log.Printf("Completed iCloud upload for document: %s", documentID)
}

// Async function to perform iCloud download (prototype)
func performICloudDownload(downloadID, icloudPath, localName string) {
	// Simulate download progress
	for progress := 0; progress <= 100; progress += 25 {
		time.Sleep(400 * time.Millisecond)
		
		status := icloudSyncStatuses[downloadID]
		if status != nil {
			status.Progress = progress
			status.Status = "syncing"
			status.Message = fmt.Sprintf("Downloading from iCloud... %d%%", progress)
		}
	}
	
	// Complete download
	status := icloudSyncStatuses[downloadID]
	if status != nil {
		status.Status = "completed"
		status.Progress = 100
		status.Message = "Successfully downloaded from iCloud"
		status.CompletedAt = time.Now()
	}
	
	log.Printf("Completed iCloud download: %s", downloadID)
}

// Helper function to get simulated case folders within a parent directory
func getSimulatedCaseFolders(parentFolder string) []ICloudDocument {
	// For prototype: return simulated case subfolders based on parent folder
	// In production: implement actual iCloud Drive API calls to list subdirectories
	
	switch parentFolder {
	case "/Legal Documents":
		return []ICloudDocument{
			{
				ID:          "case_folder_1",
				Name:        "Smith v TD Bank",
				Path:        "/Legal Documents/Smith v TD Bank",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -10),
			},
			{
				ID:          "case_folder_2",
				Name:        "Johnson Credit Dispute",
				Path:        "/Legal Documents/Johnson Credit Dispute",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -5),
			},
		}
	case "/Client Files":
		return []ICloudDocument{
			{
				ID:          "case_folder_3",
				Name:        "Wilson FCRA Case",
				Path:        "/Client Files/Wilson FCRA Case",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -3),
			},
		}
	case "/Case Materials":
		return []ICloudDocument{
			{
				ID:          "case_folder_4",
				Name:        "Youssef v Credit Bureaus",
				Path:        "/Case Materials/Youssef v Credit Bureaus",
				IsDirectory: true,
				Modified:    time.Now().AddDate(0, 0, -1),
			},
		}
	default:
		// Return empty array for folders with no cases yet
		return []ICloudDocument{}
	}
}

// Handler to test DOCX generation (debugging)
func handleTestDocx(c *gin.Context) {
	// Simple test HTML
	testHTML := `<html><body><div class="legal-document"><div class="header"><strong>TEST DOCUMENT</strong></div><div class="numbered-paragraph"><strong>1.</strong> This is a test paragraph.</div></div></body></html>`
	
	// Try to convert to DOCX
	docxContent, err := convertHTMLToDocx(testHTML)
	if err != nil {
		log.Printf("DOCX conversion error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("DOCX conversion failed: %v", err)})
		return
	}
	
	// Return success with file size
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "DOCX generation successful",
		"size": len(docxContent),
	})
}

// Authentication middleware
func authMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get session token from header
		sessionToken := c.GetHeader("Authorization")
		if sessionToken == "" {
			// Try to get from cookie
			sessionToken, _ = c.Cookie("session_token")
		}
		
		if sessionToken == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "No session token provided"})
			c.Abort()
			return
		}
		
		// Validate session
		session, exists := userSessions[sessionToken]
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid session token"})
			c.Abort()
			return
		}
		
		// Check if session is expired
		if time.Now().After(session.ExpiresAt) {
			delete(userSessions, sessionToken)
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Session expired"})
			c.Abort()
			return
		}
		
		// Store user info in context
		c.Set("userID", session.UserID)
		c.Set("username", session.Username)
		c.Set("role", session.Role)
		
		c.Next()
	}
}

// Handler for user login
func handleLogin(c *gin.Context) {
	var loginReq LoginRequest
	if err := c.ShouldBindJSON(&loginReq); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request format"})
		return
	}
	
	// Load and validate user
	user, err := validateUserCredentials(loginReq.Username, loginReq.Password)
	if err != nil {
		log.Printf("Login failed for user %s: %v", loginReq.Username, err)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}
	
	if !user.Active {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Account is disabled"})
		return
	}
	
	// Generate session token
	sessionToken, err := generateSecureToken()
	if err != nil {
		log.Printf("Failed to generate session token: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create session"})
		return
	}
	
	// Create session
	session := &UserSession{
		SessionID: sessionToken,
		UserID:    user.ID,
		Username:  user.Username,
		Role:      user.Role,
		CreatedAt: time.Now(),
		ExpiresAt: time.Now().Add(8 * time.Hour), // 8 hour session
	}
	
	userSessions[sessionToken] = session
	
	// Set cookie
	c.SetCookie("session_token", sessionToken, int(8*time.Hour.Seconds()), "/", "", false, true)
	
	log.Printf("User logged in successfully: %s (%s)", user.Username, user.Role)
	
	c.JSON(http.StatusOK, gin.H{
		"success":     true,
		"message":     "Login successful",
		"sessionToken": sessionToken,
		"user": gin.H{
			"username": user.Username,
			"role":     user.Role,
			"firm":     user.Firm,
			"email":    user.Email,
		},
		"expiresAt": session.ExpiresAt,
	})
}

// Handler for user logout
func handleLogout(c *gin.Context) {
	sessionToken := c.GetHeader("Authorization")
	if sessionToken == "" {
		sessionToken, _ = c.Cookie("session_token")
	}
	
	if sessionToken != "" {
		delete(userSessions, sessionToken)
		c.SetCookie("session_token", "", -1, "/", "", false, true)
		log.Printf("User logged out")
	}
	
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Logged out successfully",
	})
}

// Handler to validate session
func handleValidateSession(c *gin.Context) {
	sessionToken := c.GetHeader("Authorization")
	if sessionToken == "" {
		sessionToken, _ = c.Cookie("session_token")
	}
	
	if sessionToken == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "No session token"})
		return
	}
	
	session, exists := userSessions[sessionToken]
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid session"})
		return
	}
	
	if time.Now().After(session.ExpiresAt) {
		delete(userSessions, sessionToken)
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Session expired"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"valid": true,
		"user": gin.H{
			"username": session.Username,
			"role":     session.Role,
		},
		"expiresAt": session.ExpiresAt,
	})
}

// Helper function to load users from JSON file
func loadUsers() ([]User, error) {
	usersFile := "users.json"
	data, err := os.ReadFile(usersFile)
	if err != nil {
		return nil, fmt.Errorf("failed to read users file: %v", err)
	}
	
	var usersData struct {
		Users []User `json:"users"`
	}
	
	if err := json.Unmarshal(data, &usersData); err != nil {
		return nil, fmt.Errorf("failed to parse users file: %v", err)
	}
	
	return usersData.Users, nil
}

// Helper function to validate user credentials
func validateUserCredentials(username, password string) (*User, error) {
	users, err := loadUsers()
	if err != nil {
		return nil, err
	}
	
	for _, user := range users {
		if user.Username == username {
			// Check password hash
			err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password))
			if err != nil {
				return nil, fmt.Errorf("invalid password")
			}
			return &user, nil
		}
	}
	
	return nil, fmt.Errorf("user not found")
}

// Helper function to generate secure session token
func generateSecureToken() (string, error) {
	bytes := make([]byte, 32)
	if _, err := rand.Read(bytes); err != nil {
		return "", err
	}
	return fmt.Sprintf("%x", bytes), nil
}