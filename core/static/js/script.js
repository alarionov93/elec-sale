/**
 * Created by sanya on 17.03.16.
 */

;

// Object.prototype.equals = function(obj) {
//     for(var key in obj) {
//         if(obj.hasOwnProperty(key) && this.hasOwnProperty(key)) {
//             if(this[key] != obj[key]) {
//                 return false;
//             }
//         }
//     }
//     return true;
// }

VM = new ViewModel();
ko.applyBindings(VM);
// VM.init();