(import "balance_ex/balance.bin" 'balancelib)

(load-native-lib balancelib)

; Set to 1 to monitor some debug variables using the extension ext-euc-dbg
(define debug 1)

; config
(def can-id 2)

; state
(def log-running false)
(def log-thd-id nil)
(def last-can-id -1)

@const-start

(defun debug-loop ()
    (loopwhile t
        (progn
            (define setpoint (ext-balance-dbg 2))
            (define tt-filtered-current (ext-balance-dbg 3))
            (define integral (ext-balance-dbg 14))
            (sleep 0.1)
)))

; Local data to log
;
; Format
; (optKey optName optUnit optPrecision optIsRel optIsTime value-function)
;
; All entries except value-function are optional and
; default values will be used if they are left out.
(def log-fields '(
        ("kmh_vesc" "km/h" "Speed VESC" (* (get-speed) 3.6))
        ("Input Voltage" "V"            (get-vin))
        ("Current" "A"                  (get-current))
        ("Current filtered" "A"         (get-current 1))
        ("Current dir" "A"              (get-current-dir))
        ("Current In" "A"               (get-current-in))
        ("Duty"                         (get-duty))
        ("RPM"                          (get-rpm))
        ("Temp Fet" "degC" 1            (get-temp-fet))
        ("roll"                         (ix (get-imu-rpy) 0))
        ("pitch"                        (ix (get-imu-rpy) 1))
        ("yaw"                          (ix (get-imu-rpy) 2))
        ("roll_deg"    3                (rad2deg (ix (get-imu-rpy) 0)))
        ("pitch_deg"   3                (rad2deg (ix (get-imu-rpy) 1)))
        ("wh" "Wh"                      (get-wh))
        ("erpm_accel"                   (ext-balance-get-erpm-accel))
        ("erpm_accel / current"         (ext-balance-get-erpm-accel-div-current))
        ;; pid stuff
        ("pid_p"                        (ext-balance-get-p))
        ("pid_i"                        (ext-balance-get-i))
        ("pid_d"                        (ext-balance-get-d))
        ("pid_ratep"                    (ext-balance-get-ratep))
        ("pid_ratei"                    (ext-balance-get-ratei))
        ("pid_rated"                    (ext-balance-get-rated))
        ("pid_value"                    (ext-balance-get-pid))
        ("pid_rate_value"               (ext-balance-get-pid_rate))
        ; raw imu stuff
        ("acc_x"                         (ix (get-imu-acc) 0))
        ("acc_y"                         (ix (get-imu-acc) 1))
        ("acc_z"                         (ix (get-imu-acc) 2))
        ("gyro_x"                        (ix (get-imu-gyro) 0))
        ("gyro_y"                        (ix (get-imu-gyro) 1))
        ("gyro_z"                        (ix (get-imu-gyro) 2))
))


(defun loglist-parse (id lst res-fun)
    (looprange row 0 (length lst)
        (let (
                (field (ix lst row))
                (get-field
                    (fn (type default)
                        (let ((f (first field)))
                            (if (eq (type-of f) type)
                                (progn
                                    (setvar 'field (rest field))
                                    f
                                )
                                default
                ))))
                (key       (get-field type-array (str-from-n row "Field %d")))
                (unit      (get-field type-array ""))
                (name      (get-field type-array key))
                (precision (get-field type-i 2))
                (is-rel    (get-field type-symbol false))
                (is-time   (get-field type-symbol false))
            )
            (res-fun
                id ; CAN id
                row ; Field
                key ; Key
                name ; Name
                unit ; Unit
                precision ; Precision
                is-rel ; Is relative
                is-time ; Is timestamp
            )
)))

; Confiure all log fields based on loglist lst
(defun log-configure (id lst) (loglist-parse id lst 'log-config-field))

; Print all parsed fields of loglist lst
(defun print-loglist (lst) (loglist-parse 0 lst
        (fn (id row key name unit precision is-rel is-time)
            (print (list key name unit precision is-rel is-time (ix (ix lst row) -1)))
)))

(defun log-thd (id rate lst)
    (loopwhile log-running
        (progn
            (log-send-f32 id 0
                (map
                    (fn (x) (eval (ix x -1)))
                    lst
                )
            )
            (sleep (/ 1.0 rate))
)))

(defun start-log (append-gnss rate)
    (progn
        (if log-running 
            (stop-log)
            nil)

        (log-configure can-id log-fields)
        (log-start
            can-id ; CAN id
            (length log-fields) ; Field num
            rate ; Rate Hz
            true ; Append time
            append-gnss ; Append gnss
        )

        (def log-running true)
        (def log-thd-id (spawn log-thd can-id rate log-fields))
        (print "Log Started")
))

(defun stop-log () {
    (def log-running false)
    (wait log-thd-id)
    (log-stop can-id)
    (print "Log Stopped")
})


@const-end

(debug-loop)