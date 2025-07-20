// import { spawn } from 'child_process'
// import path from 'path'

// export class PythonBridge {
//   private pythonPath: string
//   private sharedPath: string

//   constructor() {
//     this.pythonPath = process.env.PYTHON_PATH || 'python3'
//     this.sharedPath = path.join(process.cwd(), '../../shared')
//   }

//   async callPythonService(serviceName: string, methodName: string, args: any[]): Promise<any> {
//     return new Promise((resolve, reject) => {
//       // Convert args to JSON strings, handling special cases
//       const jsonArgs = args.map(arg => {
//         if (typeof arg === 'string') {
//           return `"${arg}"`
//         }
//         return JSON.stringify(arg)
//       }).join(', ')

//       const script = `
// import sys
// import os
// import json
// sys.path.append('${this.sharedPath}')

// try:
//     from business_logic.services.${serviceName} import ${serviceName}
//     from business_logic.services.database_service import DatabaseService
    
//     # Initialize database service
//     db_service = DatabaseService()
//     service = ${serviceName}(db_service)
    
//     # Call the method
//     result = service.${methodName}(${jsonArgs})
    
//     # Convert result to JSON
//     if result is None:
//         print("RESULT:null")
//     elif isinstance(result, (dict, list)):
//         print("RESULT:" + json.dumps(result))
//     else:
//         print("RESULT:" + str(result))
        
// except Exception as e:
//     print("ERROR:" + str(e))
//     sys.exit(1)
//       `

//       const pythonProcess = spawn(this.pythonPath, ['-c', script])
      
//       let output = ''
//       let error = ''

//       pythonProcess.stdout.on('data', (data) => {
//         output += data.toString()
//       })

//       pythonProcess.stderr.on('data', (data) => {
//         error += data.toString()
//       })

//       pythonProcess.on('close', (code) => {
//         if (code === 0) {
//           const resultMatch = output.match(/RESULT:([\s\S]*)/)
//           if (resultMatch) {
//             const resultStr = resultMatch[1].trim()
//             if (resultStr === 'null') {
//               resolve(null)
//             } else {
//               try {
//                 const result = JSON.parse(resultStr)
//                 resolve(result)
//               } catch {
//                 resolve(resultStr)
//               }
//             }
//           } else {
//             resolve(output.trim())
//           }
//         } else {
//           const errorMatch = output.match(/ERROR:([\s\S]*)/)
//           if (errorMatch) {
//             reject(new Error(errorMatch[1].trim()))
//           } else {
//             reject(new Error(`Python process failed: ${error}`))
//           }
//         }
//       })
//     })
//   }

//   // Convenience methods for each service
//   async getUser(teleId: string) {
//     return this.callPythonService('UserService', 'getUser', [teleId])
//   }

//   async setUser(teleId: string, username: string) {
//     return this.callPythonService('UserService', 'setUser', [teleId, username])
//   }

//   async updateUsername(teleId: string, username: string) {
//     return this.callPythonService('UserService', 'updateUsername', [teleId, username])
//   }

//   async setUserSleepPreferences(teleId: string, sleepStart: string, sleepEnd: string) {
//     return this.callPythonService('UserService', 'setUserSleepPreferences', [teleId, sleepStart, sleepEnd])
//   }

//   async getEvent(eventId: string) {
//     return this.callPythonService('EventService', 'getEvent', [eventId])
//   }

//   async createEvent(name: string, description: string, startDate: string, endDate: string, creatorTeleId: string) {
//     return this.callPythonService('EventService', 'create_event', [name, description, startDate, endDate, creatorTeleId])
//   }

//   async getEventBestTime(eventId: string) {
//     return this.callPythonService('EventService', 'get_event_best_time', [eventId])
//   }

//   async getUserAvailability(teleId: string, eventId: string) {
//     return this.callPythonService('AvailabilityService', 'getUserAvailability', [teleId, eventId])
//   }

//   async updateUserAvailability(teleId: string, eventId: string, availabilityData: any[]) {
//     return this.callPythonService('AvailabilityService', 'updateUserAvailability', [teleId, eventId, availabilityData])
//   }

//   async getEventAvailability(eventId: string) {
//     return this.callPythonService('AvailabilityService', 'getEventAvailability', [eventId])
//   }
// } 