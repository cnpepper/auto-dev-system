import * as React from "react"
import { cn } from "@/lib/utils"

interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  onCheckedChange?: (checked: boolean) => void
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, onCheckedChange, onChange, checked, defaultChecked, ...props }, ref) => {
    const [isChecked, setIsChecked] = React.useState(defaultChecked || false)
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newChecked = e.target.checked
      setIsChecked(newChecked)
      onCheckedChange?.(newChecked)
      onChange?.(e)
    }

    return (
      <label className={cn(
        "relative inline-flex items-center cursor-pointer",
        props.disabled && "cursor-not-allowed opacity-50"
      )}>
        <input
          type="checkbox"
          className="sr-only peer"
          ref={ref}
          checked={checked !== undefined ? checked : isChecked}
          onChange={handleChange}
          {...props}
        />
        <div className={cn(
          "w-9 h-5 bg-input rounded-full peer transition-colors",
          "peer-focus-visible:outline-none peer-focus-visible:ring-2 peer-focus-visible:ring-ring peer-focus-visible:ring-offset-2",
          "peer-checked:bg-primary",
          "after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-background after:rounded-full after:h-4 after:w-4 after:transition-transform",
          "peer-checked:after:translate-x-4",
          className
        )} />
      </label>
    )
  }
)
Switch.displayName = "Switch"

export { Switch }
