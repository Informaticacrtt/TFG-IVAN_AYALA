<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class FormValidateRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     *
     * @return bool
     */
    public function authorize()
    {
        return true;
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array
     */
    public function rules()
    {
        $rules = [
            'username' => 'required_without:userID',
            'userID' => 'required_without:username',
        ];

        return $rules;
    }
    public function messages()
    {
        return [
            'username.required' => 'El :attribute es obligatorio.',
            'userID.required' => 'El :attribute es obligatorio.',
        ];
    }
    public function attributes()
    {
        return [
            'username' => 'username',
            'userID' => 'userID',
        ];
    }
}
